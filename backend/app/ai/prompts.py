"""Prompt templates for the Gemini provider.

Kept separate so prompts can be tuned without touching provider code.
All prompts demand strict JSON so responses parse deterministically.
"""

CATEGORY_LIST = (
    "Roads, Water Supply, Electricity, Drainage, Garbage, Healthcare, "
    "Education, Street Lights, Public Transport, Public Safety, "
    "Government Services, Others"
)

RELEVANCE_PROMPT = """You are a STRICT civic-governance content filter for a citizen grievance platform.

Accept ONLY a genuine PUBLIC GOVERNANCE / civic ISSUE or COMPLAINT — a real-world
problem about infrastructure, utilities, public services, safety, health, education,
sanitation, pollution or government services (e.g. potholes, drainage overflow, power
cut, garbage not collected, hospital bed shortage, school damage, live wire, sewage,
faulty government service).

REJECT anything else, including: general questions, entertainment (movies, songs, web
series, celebrities), sports scores/results, gaming (e.g. "how to play"), shopping or
product recommendations ("best phone under 20000"), dating, jokes, personal opinions,
random chat, spam and abuse. When in doubt, REJECT. A question that is not a civic
complaint (e.g. "Who won the cricket match?") must be rejected.

Return ONLY strict JSON, no markdown:
{{"is_relevant": true/false, "reason": "<one short sentence>", "matched_category": "<one of: {categories}, or null>"}}

TEXT:
\"\"\"{text}\"\"\"
"""

ANALYSIS_PROMPT = """You are an AI analyst for a civic grievance platform. Analyse the complaint below.

Choose category from EXACTLY this list: {categories}.
Choose urgency from EXACTLY: Low, Medium, High, Emergency.
Set is_emergency=true only for life/safety-threatening situations
(flood, fire, building/bridge collapse, major accident, gas leak, water contamination, disease outbreak).

Return ONLY strict JSON, no markdown:
{{"category": "<category>", "urgency": "<urgency>", "summary": "<max 30 words>", "reason": "<why this category & urgency, max 30 words>", "is_emergency": true/false}}

COMPLAINT:
\"\"\"{text}\"\"\"
"""

TRANSLATE_PROMPT = """Translate the following text to {target_language}.
Return ONLY the translated text, nothing else. If it is already in {target_language}, return it unchanged.

TEXT:
\"\"\"{text}\"\"\"
"""

DETECT_PROMPT = """Identify the ISO 639-1 language code of the text below
(e.g. en, hi, te, ta, kn, ml, mr, bn). Return ONLY the two-letter code.

TEXT:
\"\"\"{text}\"\"\"
"""
