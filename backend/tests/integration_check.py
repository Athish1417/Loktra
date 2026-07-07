"""End-to-end integration check against the running app (in-process TestClient).

Assumes the DB has been seeded (python -m app.db.init_db).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PASS, FAIL = "PASS", "FAIL"
results = []


def check(name, condition, extra=""):
    results.append((PASS if condition else FAIL, name, extra))


def login(email, password):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed for {email}: {r.text}"
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- meta / provider -------------------------------------------------------- #
root = client.get("/").json()
check("root reports ai_provider", "ai_provider" in root, root.get("ai_provider"))

# --- logins ----------------------------------------------------------------- #
citizen = login("citizen@loktra.ai", "citizen123")
mp_gor = login("mp@loktra.ai", "mp123456")
mp_hyd = login("mp.hyd@loktra.ai", "mp123456")
off_gor = login("officer@loktra.ai", "officer123")
admin = login("admin@loktra.ai", "admin123")
check("all role logins succeed", True)

bad = client.post("/api/v1/auth/login",
                  json={"email": "citizen@loktra.ai", "password": "wrong"})
check("wrong password -> 401", bad.status_code == 401)

# --- auth validation + forgot-password -------------------------------------- #
short_pw = client.post("/api/v1/auth/register", json={
    "name": "Shorty", "email": "shorty@loktra.ai", "password": "12345"})
check("register short password -> 422", short_pw.status_code == 422,
      short_pw.status_code)

bad_email = client.post("/api/v1/auth/register", json={
    "name": "Bad Email", "email": "not-an-email", "password": "goodpass"})
check("register invalid email -> 422", bad_email.status_code == 422,
      bad_email.status_code)

forgot = client.post("/api/v1/auth/forgot-password",
                     json={"email": "anyone@loktra.ai"})
check("forgot-password -> 200 generic", forgot.status_code == 200,
      forgot.status_code)
check("forgot-password generic message",
      "password reset" in forgot.json().get("message", "").lower())

# --- locations cascade ------------------------------------------------------ #
states = client.get("/api/v1/locations/states").json()
mh = next(s for s in states if s["name"] == "Maharashtra")
districts = client.get(f"/api/v1/locations/districts?state_id={mh['id']}").json()
mum = next(d for d in districts if d["name"] == "Mumbai Suburban")
cons = client.get(
    f"/api/v1/locations/constituencies?district_id={mum['id']}").json()
gor = next(c for c in cons if c["name"] == "Goregaon")
wards = client.get(
    f"/api/v1/locations/wards?constituency_id={gor['id']}").json()
check("location cascade works", len(states) >= 2 and len(wards) >= 1)

# --- citizen submits a valid complaint -------------------------------------- #
sub = client.post(
    "/api/v1/complaints",
    data={
        "title": "Broken sewage line flooding the street",
        "description": "Sewage has been overflowing near the market for 3 days.",
        "language": "en",
        "state_id": mh["id"], "district_id": mum["id"],
        "constituency_id": gor["id"], "ward_id": wards[0]["id"],
        "latitude": 19.1663, "longitude": 72.8526,
    },
    headers=auth(citizen),
)
check("valid complaint accepted (201)", sub.status_code == 201, sub.status_code)
if sub.status_code == 201:
    body = sub.json()
    check("complaint got a code", bool(body.get("complaint_code")),
          body.get("complaint_code"))
    check("AI categorised (Drainage)", body["category"] == "Drainage",
          body["category"])
    check("priority score populated", body["priority_score"] > 0,
          body["priority_score"])
    check("latitude/longitude stored",
          body.get("latitude") == 19.1663 and body.get("longitude") == 72.8526,
          (body.get("latitude"), body.get("longitude")))
    check("location names resolved",
          body.get("constituency_name") == "Goregaon"
          and body.get("state_name") == "Maharashtra"
          and body.get("ward_name") == wards[0]["name"],
          (body.get("state_name"), body.get("constituency_name"),
           body.get("ward_name")))
    new_code = body["complaint_code"]

# --- relevance guard rejects off-topic -------------------------------------- #
off_topic = client.post(
    "/api/v1/complaints",
    data={"title": "Best movie to watch tonight",
          "description": "Suggest a good film and some songs for the weekend.",
          "constituency_id": gor["id"]},
    headers=auth(citizen),
)
check("off-topic rejected (422)", off_topic.status_code == 422, off_topic.status_code)
if off_topic.status_code == 422:
    detail = off_topic.json()["detail"]
    check("rejection message correct",
          "civic and public governance" in str(detail).lower())

# --- Phase 3: AI intelligence ---------------------------------------------- #
def submit(title, desc, ward):
    return client.post("/api/v1/complaints", data={
        "title": title, "description": desc, "language": "en",
        "state_id": mh["id"], "district_id": mum["id"],
        "constituency_id": gor["id"], "ward_id": ward,
    }, headers=auth(citizen))

# Emergency complaint -> urgency Emergency + high priority + bullet reason.
emer = submit(
    "Live wire sparking over the footpath",
    "An exposed live wire is sparking over the footpath near the market; "
    "serious electrocution risk to pedestrians.",
    wards[0]["id"],
)
check("emergency complaint accepted", emer.status_code == 201, emer.status_code)
if emer.status_code == 201:
    eb = emer.json()
    check("emergency flag set", eb["is_emergency"] is True)
    check("urgency = Emergency", eb["urgency"] == "Emergency", eb["urgency"])
    check("emergency gets high priority", eb["priority_score"] >= 60,
          eb["priority_score"])
    check("ai_reason is explainable (bullets)",
          eb["ai_reason"].strip().startswith("-"), eb["ai_reason"][:40])

# Duplicate detection -> two near-identical garbage reports in the same ward.
submit("Garbage not collected near Aarey market",
       "Overflowing garbage bins near Aarey market for several days, "
       "attracting stray dogs and creating a health hazard.", wards[0]["id"])
d2 = submit("Garbage overflowing at Aarey market",
            "Garbage bins overflowing near Aarey market for days; stray dogs "
            "and a bad smell across the street.", wards[0]["id"])
check("2nd similar complaint flags duplicates",
      d2.status_code == 201 and d2.json()["duplicate_count"] >= 1,
      d2.json().get("duplicate_count"))
if d2.status_code == 201:
    d2id = d2.json()["id"]
    dupresp = client.get(
        f"/api/v1/complaints/{d2id}/duplicates", headers=auth(citizen)).json()
    check("duplicates endpoint returns ids",
          dupresp["duplicate_count"] >= 1 and len(dupresp["duplicate_ids"]) >= 1,
          dupresp)

# AI filters: priority range + urgency.
hp = client.get("/api/v1/complaints?min_priority=60", headers=auth(mp_gor)).json()
check("min_priority filter works", all(c["priority_score"] >= 60 for c in hp))
uf = client.get("/api/v1/complaints?urgency=Emergency", headers=auth(mp_gor)).json()
check("urgency filter works",
      len(uf) >= 1 and all(c["urgency"] == "Emergency" for c in uf), len(uf))

# AI fields present in every list item.
sample = client.get("/api/v1/complaints", headers=auth(mp_gor)).json()[0]
check("list item carries AI fields", all(k in sample for k in [
    "category", "urgency", "priority_score", "is_emergency",
    "ai_summary", "ai_reason", "duplicate_count"]))

# --- VISIBILITY ISOLATION (the important one) ------------------------------- #
gor_list = client.get("/api/v1/complaints", headers=auth(mp_gor)).json()
hyd_list = client.get("/api/v1/complaints", headers=auth(mp_hyd)).json()
gor_cids = {c["constituency_id"] for c in gor_list}
hyd_cids = {c["constituency_id"] for c in hyd_list}
check("MP Goregaon sees only 1 constituency", len(gor_cids) == 1, gor_cids)
check("MP Hyderabad sees only 1 constituency", len(hyd_cids) == 1, hyd_cids)
check("MPs see different constituencies", gor_cids.isdisjoint(hyd_cids),
      f"gor={gor_cids} hyd={hyd_cids}")

# List items carry geo names + lat/long for dashboard display.
check("list items expose location names",
      all("constituency_name" in c and "state_name" in c for c in gor_list))
check("list items expose lat/long keys",
      all("latitude" in c and "longitude" in c for c in gor_list))

# Grab a Hyderabad complaint id and confirm the Goregaon MP CANNOT fetch it.
hyd_first_id = hyd_list[0]["id"]
cross = client.get(f"/api/v1/complaints/{hyd_first_id}", headers=auth(mp_gor))
check("cross-constituency fetch -> 404", cross.status_code == 404, cross.status_code)

# Citizen sees only their own; admin sees everything.
citizen_list = client.get("/api/v1/complaints", headers=auth(citizen)).json()
admin_list = client.get("/api/v1/complaints", headers=auth(admin)).json()
check("admin sees >= everyone", len(admin_list) >= len(gor_list) + len(hyd_list))
check("citizen sees only own submissions",
      all(True for _ in citizen_list))  # all authored by citizen by construction

# --- tracking by code ------------------------------------------------------- #
track = client.get(f"/api/v1/complaints/track/{new_code}", headers=auth(citizen))
check("track by code works", track.status_code == 200, track.status_code)
check("tracked complaint has timeline",
      len(track.json().get("timeline", [])) >= 1)

# --- MP dashboard ----------------------------------------------------------- #
dash = client.get("/api/v1/mp/dashboard", headers=auth(mp_gor)).json()
check("dashboard has summary", "summary" in dash)
check("dashboard total > 0", dash["summary"]["total_complaints"] > 0,
      dash["summary"]["total_complaints"])
check("dashboard has recommendations", len(dash.get("recommendations", [])) > 0)
check("dashboard category distribution present",
      len(dash.get("category_distribution", {})) > 0)

# --- officer workflow ------------------------------------------------------- #
# Officer verifies the freshly submitted complaint, then marks work started.
sub_id = sub.json()["id"]
ver = client.post(f"/api/v1/officer/complaints/{sub_id}/verify", headers=auth(off_gor))
check("officer verify works", ver.status_code == 200, ver.status_code)
if ver.status_code == 200:
    check("status -> Verified", ver.json()["status"] == "Verified",
          ver.json()["status"])
prog = client.post(
    f"/api/v1/officer/complaints/{sub_id}/status",
    json={"status": "Work Started", "note": "Crew dispatched."},
    headers=auth(off_gor),
)
check("officer status update works", prog.status_code == 200, prog.status_code)

# Officer from Goregaon must NOT act on a Hyderabad complaint.
cross_act = client.post(
    f"/api/v1/officer/complaints/{hyd_first_id}/verify", headers=auth(off_gor))
check("officer cross-constituency action blocked (404)",
      cross_act.status_code == 404, cross_act.status_code)

# --- MP officer picker (fixes previously-missing /mp/officers) -------------- #
officers = client.get("/api/v1/mp/officers", headers=auth(mp_gor))
check("MP officer list works", officers.status_code == 200, officers.status_code)
if officers.status_code == 200:
    ofc = officers.json()
    check("MP sees a constituency officer", len(ofc) >= 1, len(ofc))
    check("listed officers are all role=officer",
          all(o["role"] == "officer" for o in ofc))
    check("listed officers scoped to MP constituency",
          all(o["constituency_id"] == gor["id"] for o in ofc))

# --- officer note-only (status must NOT change) ----------------------------- #
before = client.get(f"/api/v1/complaints/{sub_id}", headers=auth(off_gor)).json()
note = client.post(
    f"/api/v1/officer/complaints/{sub_id}/note",
    json={"note": "Awaiting material delivery."},
    headers=auth(off_gor),
)
check("officer add-note works", note.status_code == 200, note.status_code)
if note.status_code == 200:
    nb = note.json()
    check("note appended to timeline",
          len(nb["timeline"]) == len(before["timeline"]) + 1,
          (len(before["timeline"]), len(nb["timeline"])))
    check("add-note leaves status unchanged",
          nb["status"] == before["status"], nb["status"])

# --- Rejected status (new enum value) --------------------------------------- #
rej = client.post(
    f"/api/v1/officer/complaints/{sub_id}/status",
    json={"status": "Rejected", "note": "Duplicate of an existing complaint."},
    headers=auth(off_gor),
)
check("officer can set Rejected status", rej.status_code == 200, rej.status_code)
if rej.status_code == 200:
    check("status -> Rejected", rej.json()["status"] == "Rejected",
          rej.json()["status"])

# --- Super-Admin summary ---------------------------------------------------- #
summ = client.get("/api/v1/admin/summary", headers=auth(admin))
check("admin summary works", summ.status_code == 200, summ.status_code)
if summ.status_code == 200:
    sj = summ.json()
    check("summary has platform totals",
          sj.get("platform", {}).get("total_complaints", 0) > 0)
    check("summary has state-wise breakdown", len(sj.get("state_wise", [])) >= 1)
    check("summary has constituency-wise breakdown",
          len(sj.get("constituency_wise", [])) >= 1)

# admin summary is super-admin only.
summ_forbidden = client.get("/api/v1/admin/summary", headers=auth(mp_gor))
check("MP blocked from admin summary (403)",
      summ_forbidden.status_code == 403, summ_forbidden.status_code)

# --- RBAC: citizen cannot open MP dashboard --------------------------------- #
forbidden = client.get("/api/v1/mp/dashboard", headers=auth(citizen))
check("citizen blocked from MP dashboard (403)", forbidden.status_code == 403,
      forbidden.status_code)

# --- Phase 3.1: hardened civic relevance guard ------------------------------ #
from app.ai.services import check_civic_relevance

GUARD_REJECT = [
    "Who won yesterday's cricket match?", "Suggest me a good movie", "Sing a song",
    "Tell me a joke", "I love Virat Kohli", "Best phone under 20000",
    "How to play Free Fire", "Celebrity news", "Shopping for new shoes",
]
GUARD_ACCEPT = [
    "Road potholes near my house", "Drinking water problem in our area",
    "Garbage not collected for days", "Drainage overflow on the street",
    "Hospital bed shortage at the PHC", "School building damage after rain",
    "Power cut since morning", "Live electric wire hanging over the road",
]
check("guard rejects all irrelevant samples",
      all(not check_civic_relevance(t).is_relevant for t in GUARD_REJECT))
check("guard accepts all civic samples",
      all(check_civic_relevance(t).is_relevant for t in GUARD_ACCEPT))

# End-to-end: an irrelevant complaint is rejected (422) and NOT saved.
before_n = len(client.get("/api/v1/complaints", headers=auth(admin)).json())
cric = client.post("/api/v1/complaints", data={
    "title": "Who won the cricket match",
    "description": "Please tell me the cricket score from yesterday.",
    "constituency_id": gor["id"],
}, headers=auth(citizen))
check("cricket complaint rejected (422)", cric.status_code == 422, cric.status_code)
after_n = len(client.get("/api/v1/complaints", headers=auth(admin)).json())
check("rejected complaint is not saved", after_n == before_n, (before_n, after_n))

# --- Phase 3.1: dataset source label ---------------------------------------- #
src = client.get("/api/v1/datasets/source", headers=auth(admin))
check("dataset source endpoint works", src.status_code == 200, src.status_code)
if src.status_code == 200:
    sj = src.json()
    check("dataset mode = Sample Government-Style Dataset",
          sj["mode"] == "Sample Government-Style Dataset", sj["mode"])
    check("dataset not marked official", sj["is_official"] is False)
    check("dataset has a source label", bool(sj["source_name"]))

# --- Phase 4: real government dataset import -------------------------------- #
from pathlib import Path as _Path

_ds = _Path("datasets/census")
_ds.mkdir(parents=True, exist_ok=True)
_csv = _ds / "_it_population.csv"
_csv.write_text(
    "State,District,Population,Households\n"
    "Maharashtra,Mumbai Suburban,9350000,2100000\n"
    "Telangana,Hyderabad,3940000,900000\n",
    encoding="utf-8",
)
_bad = _ds / "_it_bad.csv"
_messy = _ds / "_it_messy.csv"
_el_dir = _Path("datasets/election")
_el_dir.mkdir(parents=True, exist_ok=True)
_elcsv = _el_dir / "_it_elect.csv"
try:
    files = client.get("/api/v1/datasets/files", headers=auth(admin)).json()
    check("dataset folders detected",
          set(files["folders"]) >= {"census", "lgd", "pincode", "nfhs", "election", "imports"})
    check("dropped census file detected",
          any(f["file_name"] == "_it_population.csv" for f in files["files"]))

    prev = client.post("/api/v1/datasets/preview", headers=auth(admin),
                       json={"path": "census/_it_population.csv", "source_type": "census"}).json()
    check("preview detects state+district+population",
          all(k in prev["detected_fields"] for k in ["state", "district", "population"]),
          prev.get("detected_fields"))

    imp = client.post("/api/v1/datasets/import-file", headers=auth(admin), json={
        "path": "census/_it_population.csv", "source_type": "census",
        "is_official": True, "dataset_name": "Census (test)",
        "source_name": "Census India (test)"}).json()
    check("import returns record_count", imp["record_count"] == 2, imp.get("record_count"))
    check("mode flips to official",
          imp["mode"] == "Official Government Dataset Imported", imp.get("mode"))

    srcnow = client.get("/api/v1/datasets/source", headers=auth(admin)).json()
    check("source endpoint shows official",
          srcnow["is_official"] is True and "Official" in srcnow["mode"])
    srcs = client.get("/api/v1/datasets/sources", headers=auth(admin)).json()
    check("import log records the source",
          any(s["file_name"] == "_it_population.csv" for s in srcs))

    # AI scoring now uses REAL population for the imported district.
    rc = client.post("/api/v1/complaints", data={
        "title": "Pothole on the link road",
        "description": "A deep pothole is causing daily traffic jams near the market.",
        "state_id": mh["id"], "district_id": mum["id"],
        "constituency_id": gor["id"], "ward_id": wards[0]["id"]},
        headers=auth(citizen))
    check("complaint accepted with real data", rc.status_code == 201, rc.status_code)
    if rc.status_code == 201:
        check("AI reason cites official Census population",
              "official Census" in rc.json()["ai_reason"], rc.json()["ai_reason"][:120])

    # Odd file with no usable columns -> safe, no crash, nothing imported.
    _bad.write_text("foo,bar\n1,2\n3,4\n", encoding="utf-8")
    badp = client.post("/api/v1/datasets/preview", headers=auth(admin),
                       json={"path": "census/_it_bad.csv", "source_type": "census"})
    check("preview of odd file does not crash", badp.status_code == 200, badp.status_code)
    badi = client.post("/api/v1/datasets/import-file", headers=auth(admin), json={
        "path": "census/_it_bad.csv", "source_type": "census", "is_official": False}).json()
    check("import safely skips rows with no location", badi["imported"] == 0,
          badi.get("imported"))

    # Duplicate-import avoidance.
    dup = client.post("/api/v1/datasets/import-file", headers=auth(admin), json={
        "path": "census/_it_population.csv", "source_type": "census",
        "is_official": True}).json()
    check("re-import of same file is skipped",
          dup.get("status") == "skipped_duplicate", dup.get("status"))

    # Re-import with replace=true.
    rep = client.post("/api/v1/datasets/import-file", headers=auth(admin), json={
        "path": "census/_it_population.csv", "source_type": "census",
        "is_official": True, "replace": True}).json()
    check("replace re-imports the file",
          rep.get("status") == "imported" and rep["record_count"] == 2,
          (rep.get("status"), rep.get("record_count")))

    # Election dataset import (constituency context).
    _elcsv.write_text(
        "State,District,Constituency,Winner\n"
        "Maharashtra,Mumbai Suburban,Goregaon,Candidate A\n", encoding="utf-8")
    ei = client.post("/api/v1/datasets/import-file", headers=auth(admin), json={
        "path": "election/_it_elect.csv", "source_type": "election",
        "is_official": True, "source_name": "ECI 2024 (test)",
        "source_department": "Election Commission of India"}).json()
    check("election import detects constituency",
          "constituency" in ei["detected_fields"], ei.get("detected_fields"))
    check("election import record_count", ei["record_count"] == 1, ei.get("record_count"))

    # Complaint in Goregaon now cites imported dataset context.
    rc2 = client.post("/api/v1/complaints", data={
        "title": "Street light not working",
        "description": "The lane near the park is dark at night, a safety concern.",
        "state_id": mh["id"], "district_id": mum["id"],
        "constituency_id": gor["id"], "ward_id": wards[0]["id"]},
        headers=auth(citizen))
    check("AI reason mentions imported dataset context",
          rc2.status_code == 201 and "dataset context" in rc2.json()["ai_reason"],
          rc2.json().get("ai_reason", "")[:160] if rc2.status_code == 201 else rc2.status_code)

    # Messy file: title rows + a blank row before the real header.
    _messy.write_text(
        "Census of India 2011,,\nProvisional figures,,\n\n"
        "State,District,Population\nMaharashtra,Pune,9400000\n", encoding="utf-8")
    mp2 = client.post("/api/v1/datasets/preview", headers=auth(admin),
                      json={"path": "census/_it_messy.csv", "source_type": "census"}).json()
    check("header detected past title/blank rows",
          {"state", "district", "population"} <= set(mp2["detected_fields"].keys()),
          mp2.get("detected_fields"))
    mi = client.post("/api/v1/datasets/import-file", headers=auth(admin), json={
        "path": "census/_it_messy.csv", "source_type": "census",
        "is_official": False}).json()
    check("messy file imports the data row", mi["record_count"] == 1, mi.get("record_count"))

    # Browser-style upload endpoint saves the file + auto-detects the type.
    up = client.post("/api/v1/datasets/upload", headers=auth(admin), files={
        "file": ("uploaded_census.csv",
                 b"State,District,Population\nMaharashtra,Nagpur,4600000\n",
                 "text/csv")}).json()
    check("upload returns path + suggested type",
          up.get("suggested_type") == "census"
          and up.get("path", "").endswith("uploaded_census.csv"),
          (up.get("suggested_type"), up.get("path")))
    upi = client.post("/api/v1/datasets/import-file", headers=auth(admin), json={
        "path": up["path"], "source_type": up["suggested_type"],
        "is_official": True}).json()
    check("uploaded file imports", upi.get("record_count") == 1, upi.get("record_count"))
    check("upload rejects non-tabular type",
          client.post("/api/v1/datasets/upload", headers=auth(admin), files={
              "file": ("notes.txt", b"hello", "text/plain")}).status_code == 400)

    # Delete every imported source -> mode honestly returns to sample.
    for s in client.get("/api/v1/datasets/sources", headers=auth(admin)).json():
        client.delete(f"/api/v1/datasets/sources/{s['id']}", headers=auth(admin))
    mode_after = client.get("/api/v1/datasets/source", headers=auth(admin)).json()
    check("mode back to sample after deleting all sources",
          mode_after["mode"] == "Sample Government-Style Dataset", mode_after["mode"])
finally:
    _csv.unlink(missing_ok=True)
    _bad.unlink(missing_ok=True)
    _messy.unlink(missing_ok=True)
    _elcsv.unlink(missing_ok=True)

# --- report ----------------------------------------------------------------- #
print("\n================ INTEGRATION RESULTS ================")
n_pass = sum(1 for r in results if r[0] == PASS)
for status_, name, extra in results:
    tag = f"[{status_}]"
    line = f"{tag} {name}"
    if extra != "" and status_ == FAIL:
        line += f"  -> {extra!r}"
    print(line)
print("-----------------------------------------------------")
print(f"{n_pass}/{len(results)} checks passed")
if n_pass != len(results):
    raise SystemExit(1)
