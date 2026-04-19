"""Research Biology/biotech faculty at a list of schools using Claude + web search.

Reads schools from schools.txt, asks Claude Opus 4.7 (with the server-side
web_search tool) to identify notable Bio/biotech faculty at each school, and
writes results to faculty_results.json, faculty_results.csv, and
faculty_results.md.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python research_faculty.py

Optional flags:
    --limit N        Only research the first N schools (useful for testing)
    --school NAME    Research just one school (exact match against schools.txt)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic

MODEL = "claude-opus-4-7"
SCHOOLS_FILE = Path(__file__).parent / "schools.txt"
OUT_JSON = Path(__file__).parent / "faculty_results.json"
OUT_CSV = Path(__file__).parent / "faculty_results.csv"
OUT_MD = Path(__file__).parent / "faculty_results.md"
OUT_JS = Path(__file__).parent / "faculty_results.js"
OUT_HTML = Path(__file__).parent / "report.html"
HTML_TEMPLATE = Path(__file__).parent / "report_template.html"

SYSTEM_PROMPT = """You are a research assistant helping a prospective student identify notable Biology and biotech faculty to reach out to for general interest outreach.

For each school you are asked about, use web search to find 4-8 currently active faculty members in Biology, biotechnology, biomedical engineering, molecular biology, genetics, biochemistry, neuroscience, bioengineering, or closely related fields who are well-known in their area. You do not need Nobel-laureate-level fame — being a recognized leader, highly-cited researcher, HHMI investigator, NAS/NAE member, endowed chair, department head, or PI of a prominent lab all qualify.

For each faculty member, gather:
- full name
- department / school affiliation
- primary research area (1 short phrase)
- 1-2 notable accomplishments (awards, discoveries, high-impact papers, lab size, funding)
- lab or faculty profile URL (prefer the official university page or lab website)
- publicly listed email if you can find it on the faculty page (do NOT guess — leave null if not clearly posted)

Prefer faculty whose research is accessible to undergraduates (teach undergrad courses, have undergraduate researchers in their lab, run summer programs).

Be accurate. If you are not confident a person is currently at the school, exclude them. Do not fabricate emails or URLs."""

USER_TEMPLATE = """Find notable Biology/biotech faculty at {school} suitable for a prospective undergraduate to contact for general-interest research outreach.

Return ONLY a JSON object matching this schema, with no prose before or after:

{{
  "school": "{school}",
  "faculty": [
    {{
      "name": "string",
      "department": "string",
      "research_area": "string",
      "notable": "string",
      "url": "string",
      "email": "string or null"
    }}
  ]
}}"""


def read_schools() -> list[str]:
    if not SCHOOLS_FILE.exists():
        sys.exit(f"Missing {SCHOOLS_FILE}. Create it with one school per line.")
    return [line.strip() for line in SCHOOLS_FILE.read_text().splitlines() if line.strip()]


def _sanitize(block: str) -> str:
    """Escape literal newlines / tabs inside JSON string values."""
    out = []
    in_string = False
    escape = False
    for c in block:
        if in_string:
            if escape:
                out.append(c); escape = False
            elif c == "\\":
                out.append(c); escape = True
            elif c == '"':
                out.append(c); in_string = False
            elif c == "\n":
                out.append("\\n")
            elif c == "\r":
                out.append("\\r")
            elif c == "\t":
                out.append("\\t")
            else:
                out.append(c)
        else:
            out.append(c)
            if c == '"':
                in_string = True
    return "".join(out)


def extract_json(text: str) -> dict | None:
    """Pull the first {...} JSON object out of a model response."""
    if not text:
        return None
    # Strip common code-fence wrappers
    for fence in ("```json", "```JSON", "```"):
        if fence in text:
            parts = text.split(fence)
            for p in parts:
                if "{" in p and "}" in p:
                    text = p
                    break
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if in_string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                block = text[start : i + 1]
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    try:
                        return json.loads(_sanitize(block))
                    except json.JSONDecodeError:
                        return None
    return None


def research_school(client: anthropic.Anthropic, school: str) -> dict:
    print(f"  -> querying Claude + web search for {school}...", flush=True)
    with client.messages.stream(
        model=MODEL,
        max_tokens=24000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": USER_TEMPLATE.format(school=school)}],
    ) as stream:
        final = stream.get_final_message()

    text_parts = [b.text for b in final.content if b.type == "text"]
    text = "\n".join(text_parts).strip()
    parsed = extract_json(text)
    if parsed is None:
        print(f"     WARN: could not parse JSON for {school}. Raw text saved.", flush=True)
        return {"school": school, "faculty": [], "_raw": text}
    parsed.setdefault("school", school)
    parsed.setdefault("faculty", [])
    print(f"     got {len(parsed['faculty'])} faculty", flush=True)
    return parsed


def write_outputs(results: list[dict]) -> None:
    OUT_JSON.write_text(json.dumps(results, indent=2))
    OUT_JS.write_text("window.FACULTY_DATA = " + json.dumps(results) + ";\n")
    if HTML_TEMPLATE.exists():
        template = HTML_TEMPLATE.read_text()
        # Inject data inline so report.html is fully self-contained
        payload = "<script>window.FACULTY_DATA = " + json.dumps(results) + ";</script>"
        rendered = template.replace('<script src="faculty_results.js"></script>', payload)
        OUT_HTML.write_text(rendered)

    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["school", "name", "department", "research_area", "notable", "url", "email"])
        for r in results:
            for fac in r.get("faculty", []):
                w.writerow([
                    r.get("school", ""),
                    fac.get("name", ""),
                    fac.get("department", ""),
                    fac.get("research_area", ""),
                    fac.get("notable", ""),
                    fac.get("url", ""),
                    fac.get("email") or "",
                ])

    lines = ["# Biology / Biotech Faculty Outreach List", ""]
    for r in results:
        lines.append(f"## {r.get('school', 'Unknown')}")
        lines.append("")
        faculty = r.get("faculty", [])
        if not faculty:
            lines.append("_No faculty returned._")
            lines.append("")
            continue
        for fac in faculty:
            name = fac.get("name", "?")
            url = fac.get("url", "")
            header = f"- **[{name}]({url})**" if url else f"- **{name}**"
            lines.append(header)
            if fac.get("department"):
                lines.append(f"  - Department: {fac['department']}")
            if fac.get("research_area"):
                lines.append(f"  - Research: {fac['research_area']}")
            if fac.get("notable"):
                lines.append(f"  - Notable: {fac['notable']}")
            if fac.get("email"):
                lines.append(f"  - Email: {fac['email']}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines))

    print(f"\nWrote:\n  {OUT_JSON}\n  {OUT_CSV}\n  {OUT_MD}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only research the first N schools")
    parser.add_argument("--school", type=str, default=None, help="Research one specific school")
    parser.add_argument("--resume", action="store_true", help="Skip schools that already have faculty in faculty_results.json")
    parser.add_argument("--retry-failed", action="store_true", help="Redo schools that had _raw or _error")
    parser.add_argument("--concurrency", type=int, default=1, help="Schools to research in parallel")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. export it and rerun.")

    schools = read_schools()
    if args.school:
        schools = [s for s in schools if s == args.school]
        if not schools:
            sys.exit(f"--school {args.school!r} not found in {SCHOOLS_FILE.name}")
    elif args.limit:
        schools = schools[: args.limit]

    client = anthropic.Anthropic()

    existing: dict[str, dict] = {}
    if (args.resume or args.retry_failed) and OUT_JSON.exists():
        for entry in json.loads(OUT_JSON.read_text()):
            existing[entry["school"]] = entry

    # Preserve existing entries not in the current run set
    results: list[dict] = list(existing.values())
    results_by_school = {r["school"]: r for r in results}

    def is_good(entry: dict | None) -> bool:
        if not entry:
            return False
        if "_raw" in entry or "_error" in entry:
            return False
        return bool(entry.get("faculty"))

    to_do: list[str] = []
    for s in schools:
        prev = existing.get(s)
        if args.resume and is_good(prev):
            continue
        if args.retry_failed and prev and is_good(prev):
            continue
        to_do.append(s)

    print(f"Researching {len(to_do)} school(s) with {MODEL} (concurrency={args.concurrency}, skipping {len(schools) - len(to_do)})\n")

    lock = threading.Lock()
    done_count = [0]

    def work(school: str) -> tuple[str, dict]:
        try:
            return school, research_school(client, school)
        except Exception as e:  # noqa: BLE001
            print(f"     ERROR: {school}: {e}", flush=True)
            return school, {"school": school, "faculty": [], "_error": str(e)}

    def commit(school: str, new_entry: dict) -> None:
        with lock:
            if school in results_by_school:
                idx = results.index(results_by_school[school])
                results[idx] = new_entry
            else:
                results.append(new_entry)
            results_by_school[school] = new_entry
            done_count[0] += 1
            print(f"[{done_count[0]}/{len(to_do)}] {school} committed", flush=True)
            write_outputs(results)

    if args.concurrency <= 1:
        for school in to_do:
            _, entry = work(school)
            commit(school, entry)
    else:
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(work, s): s for s in to_do}
            for fut in as_completed(futures):
                school, entry = fut.result()
                commit(school, entry)

    print("\nDone.")


if __name__ == "__main__":
    main()
