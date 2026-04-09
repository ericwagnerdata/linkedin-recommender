import json
import re
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PIPELINE_FILE = DATA_DIR / "pipeline.json"
PEOPLE_DIR = DATA_DIR / "people"
PIPELINE_DOC = Path(__file__).parent / "PIPELINE.md"


def ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    PEOPLE_DIR.mkdir(exist_ok=True)
    if not PIPELINE_FILE.exists():
        PIPELINE_FILE.write_text(json.dumps({"people": []}, indent=2))


def load_pipeline():
    ensure_dirs()
    return json.loads(PIPELINE_FILE.read_text(encoding="utf-8"))


def save_pipeline(data):
    PIPELINE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _write_pipeline_doc(data)


def make_id(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def add_person(name, linkedin_url=""):
    data = load_pipeline()
    person_id = make_id(name)
    for p in data["people"]:
        if p["id"] == person_id:
            return None, f"'{name}' already exists in the pipeline."
    person = {
        "id": person_id,
        "name": name,
        "linkedin_url": linkedin_url or "",
        "status": "pending",
        "added_date": str(date.today()),
        "completed_date": None,
        "people_file": str(PEOPLE_DIR / f"{person_id}.md"),
    }
    data["people"].append(person)
    save_pipeline(data)
    _init_people_file(person)
    return person, None


def get_person(name_or_id):
    data = load_pipeline()
    for p in data["people"]:
        if p["id"] == make_id(name_or_id) or p["name"].lower() == name_or_id.lower():
            return p
    return None


def mark_completed(person_id):
    data = load_pipeline()
    for p in data["people"]:
        if p["id"] == person_id:
            p["status"] = "completed"
            p["completed_date"] = str(date.today())
            break
    save_pipeline(data)


def list_people():
    data = load_pipeline()
    return data["people"]


# ── Per-person markdown ───────────────────────────────────────────────────────

def _init_people_file(person):
    path = Path(person["people_file"])
    url_line = person["linkedin_url"] if person["linkedin_url"] else "_Not set_"
    content = (
        f"# {person['name']}\n\n"
        f"**LinkedIn:** {url_line}\n"
        f"**Added:** {person['added_date']}\n"
        f"**Status:** Pending\n"
    )
    path.write_text(content, encoding="utf-8")


def update_people_file(person, answers, recommendation):
    path = Path(person["people_file"])
    url_line = person["linkedin_url"] if person["linkedin_url"] else "_Not set_"
    content = (
        f"# {person['name']}\n\n"
        f"**LinkedIn:** {url_line}\n"
        f"**Added:** {person['added_date']}\n"
        f"**Status:** Completed\n"
        f"\n---\n\n"
        f"## What You've Shared\n\n"
        f"**How you know them:** {answers['relationship']}\n\n"
        f"**Work context:** {answers['work_context']}\n\n"
        f"**Duration:** {answers['duration']}\n\n"
        f"**Skills / qualities to highlight:** {answers['skills']}\n\n"
        f"**Accomplishments:** {answers['accomplishments']}\n"
        f"\n---\n\n"
        f"## Recommendation\n\n"
        f"Written {date.today()}\n\n"
        f"{recommendation}\n"
    )
    path.write_text(content, encoding="utf-8")


# ── PIPELINE.md generation ────────────────────────────────────────────────────

def _write_pipeline_doc(data):
    people = data["people"]
    pending   = [p for p in people if p["status"] == "pending"]
    completed = [p for p in people if p["status"] == "completed"]

    def url_cell(p):
        return f"[profile]({p['linkedin_url']})" if p.get("linkedin_url") else "_TBD_"

    lines = [
        "# LinkedIn Recommendation Pipeline",
        "",
        f"_Last updated: {date.today()}_",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Stage | Count |",
        "|-------|-------|",
        f"| Pending | {len(pending)} |",
        f"| Completed | {len(completed)} |",
        f"| **Total** | **{len(people)}** |",
        "",
        "---",
        "",
        f"## Pending ({len(pending)})",
        "",
    ]

    if pending:
        lines += [
            "| Name | LinkedIn | Added |",
            "|------|----------|-------|",
        ]
        for p in pending:
            lines.append(f"| {p['name']} | {url_cell(p)} | {p['added_date']} |")
    else:
        lines.append("_No pending recommendations._")

    lines += [
        "",
        "---",
        "",
        f"## Completed ({len(completed)})",
        "",
    ]

    if completed:
        lines += [
            "| Name | LinkedIn | Completed |",
            "|------|----------|-----------|",
        ]
        for p in completed:
            lines.append(f"| {p['name']} | {url_cell(p)} | {p['completed_date']} |")
    else:
        lines.append("_No recommendations written yet._")

    lines.append("")
    PIPELINE_DOC.write_text("\n".join(lines), encoding="utf-8")
