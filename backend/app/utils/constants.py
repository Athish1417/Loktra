"""Single source of truth for civic categories, statuses, keyword banks and language maps.

Both the AI fallback and the Gemini prompts pull from here so behaviour stays consistent.
"""
import re

from app.models.complaint import ComplaintCategory, ComplaintStatusEnum, UrgencyLevel

# ---------------------------------------------------------------------------
# Languages (ISO code -> display name). Architecture allows adding more later.
# ---------------------------------------------------------------------------
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
}

# Unicode block start/end -> language, for the offline language detector.
SCRIPT_RANGES = [
    (0x0980, 0x09FF, "bn"),  # Bengali
    (0x0B80, 0x0BFF, "ta"),  # Tamil
    (0x0C00, 0x0C7F, "te"),  # Telugu
    (0x0C80, 0x0CFF, "kn"),  # Kannada
    (0x0D00, 0x0D7F, "ml"),  # Malayalam
    (0x0900, 0x097F, "hi"),  # Devanagari (Hindi/Marathi -> defaults to hi)
]

# ---------------------------------------------------------------------------
# Emergency keywords -> auto high priority + is_emergency flag.
# ---------------------------------------------------------------------------
EMERGENCY_KEYWORDS = [
    "flood", "flooding", "fire", "burning", "collapse", "collapsed",
    "building collapse", "bridge collapse", "bridge crack", "crack in bridge",
    "accident", "electrocution", "gas leak", "explosion", "hospital shortage",
    "no beds", "oxygen shortage", "medicine shortage", "outbreak", "epidemic",
    "water contamination", "contaminated water", "sewage overflow", "landslide",
    "electric shock", "live wire", "drowning", "riot", "dangerous road",
]

# ---------------------------------------------------------------------------
# Governance-relevance guard.
# ---------------------------------------------------------------------------
# If the text matches BLOCKED and no CATEGORY keyword -> rejected as off-topic.
BLOCKED_KEYWORDS = [
    "movie", "film", "cinema", "song", "music album", "actor", "actress",
    "celebrity", "cricket score", "football match", "game", "gaming",
    "dating", "girlfriend", "boyfriend", "hookup", "meme", "joke",
    "lottery win", "crypto pump", "buy followers", "sex", "porn",
    "abuse you", "idiot bot", "random chat", "entertainment", "shopping",
    "discount offer", "promo code", "subscribe", "follow me", "giveaway",
    "sale", "coupon", "celebrity news", "web series", "netflix", "reel",
    "wallpaper", "ringtone", "horoscope", "free fire", "pubg", "bgmi",
]

# ---------------------------------------------------------------------------
# Governance-context words. Their presence signals a genuine civic/public issue
# even when no specific category keyword matches (so we can accept a valid
# "Others" complaint without opening the door to random chatter).
# ---------------------------------------------------------------------------
GOVERNANCE_KEYWORDS = [
    "government", "govt", "municipal", "municipality", "corporation",
    "panchayat", "ward", "constituency", "public", "civic", "authority",
    "department", "officer", "official", "certificate", "ration", "pension",
    "aadhaar", "scheme", "subsidy", "citizen", "complaint", "grievance",
    "infrastructure", "sanitation", "pollution", "encroachment", "welfare",
    "administration", "tax", "property record", "birth certificate",
    "death certificate", "voter", "registration",
]

# ---------------------------------------------------------------------------
# Non-civic INTENT patterns (regex). These phrasings are requests/questions,
# not civic complaints (entertainment, sports scores, shopping, general chat,
# gaming). A match is a hard reject regardless of any stray keyword — this stops
# false positives like "how to play free fire" (the word 'fire' would otherwise
# look like an emergency).
# ---------------------------------------------------------------------------
IRRELEVANT_PATTERNS = [
    re.compile(p)
    for p in [
        r"\bwho\s+won\b",
        r"\b(match|cricket|football|ipl|game)\s+(score|result|won|winner)\b",
        r"\bsports?\s+scores?\b",
        r"\bscore\s+of\b",
        r"\bsuggest\s+(me\s+)?(a\s+|some\s+)?(good\s+)?(movie|film|song|game|book|restaurant|phone|laptop)",
        r"\brecommend\s+(a\s+|some\s+)?(movie|film|song|game|book|restaurant|phone|laptop)",
        r"\b(tell|give|show)\s+me\s+(a\s+|some\s+)?(joke|movie|song|story|movie\s+names?)",
        r"\bmovie\s+names?\b",
        r"\bsing\s+(a\s+|me\s+a\s+)?song\b",
        r"\bhow\s+to\s+play\b",
        r"\bbest\s+.{0,25}\bunder\s+\d",
        r"\bdating\s+(advice|tips|app|site)\b",
        r"\bwho\s+is\s+(your|the)\s+(favourite|favorite|best)\b",
    ]
]

# ---------------------------------------------------------------------------
# Category keyword bank -> offline categorisation.
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    ComplaintCategory.roads: [
        "road", "pothole", "highway", "footpath", "pavement", "speed breaker",
        "traffic signal", "bridge", "flyover",
    ],
    ComplaintCategory.water: [
        "water", "tap", "pipeline", "leakage", "no water", "supply", "borewell",
        "tanker", "contamination",
    ],
    ComplaintCategory.electricity: [
        "electricity", "power cut", "transformer", "voltage", "current",
        "wire", "meter", "outage", "load shedding",
    ],
    ComplaintCategory.drainage: [
        "drain", "drainage", "sewage", "gutter", "manhole", "overflow", "clogged",
    ],
    ComplaintCategory.garbage: [
        "garbage", "waste", "trash", "dump", "dustbin", "litter", "cleaning",
    ],
    ComplaintCategory.healthcare: [
        "hospital", "clinic", "doctor", "phc", "medicine", "ambulance",
        "health center", "dispensary", "beds",
    ],
    ComplaintCategory.education: [
        "school", "college", "teacher", "classroom", "students", "education",
        "anganwadi", "scholarship",
    ],
    ComplaintCategory.street_lights: [
        "street light", "streetlight", "lamp post", "dark street", "lighting",
    ],
    ComplaintCategory.public_transport: [
        "bus", "metro", "auto", "transport", "bus stop", "railway station", "train",
    ],
    ComplaintCategory.public_safety: [
        "safety", "crime", "theft", "harassment", "police", "accident",
        "encroachment", "stray dogs",
    ],
    ComplaintCategory.government_services: [
        "ration", "aadhaar", "certificate", "pension", "office", "document",
        "corruption", "bribe", "portal",
    ],
}

# ---------------------------------------------------------------------------
# Enum coercion helpers (map free-text AI output onto our enums safely).
# ---------------------------------------------------------------------------
def to_category(value: str) -> ComplaintCategory:
    if not value:
        return ComplaintCategory.others
    v = value.strip().lower()
    for cat in ComplaintCategory:
        if cat.value.lower() == v or cat.name.lower() == v:
            return cat
    return ComplaintCategory.others


def to_urgency(value: str) -> UrgencyLevel:
    if not value:
        return UrgencyLevel.medium
    v = value.strip().lower()
    for lvl in UrgencyLevel:
        if lvl.value.lower() == v or lvl.name.lower() == v:
            return lvl
    return UrgencyLevel.medium


def to_status(value: str) -> ComplaintStatusEnum:
    v = (value or "").strip().lower()
    for st in ComplaintStatusEnum:
        if st.value.lower() == v or st.name.lower() == v:
            return st
    raise ValueError(f"Unknown status: {value}")
