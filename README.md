# Faculty Research Tool

Researches Biology / biotech faculty at each school in `schools.txt` using Claude Opus 4.7 with web search.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
# All schools in schools.txt
python research_faculty.py

# Just the first 2 (smoke test)
python research_faculty.py --limit 2

# One specific school
python research_faculty.py --school "Brown University"
```

## Output

Three files are written (and rewritten incrementally after every school, so you can Ctrl-C safely):

- `faculty_results.json` — raw structured data
- `faculty_results.csv` — flat table for spreadsheets
- `faculty_results.md` — readable summary grouped by school

## Cost note

Each school runs Opus 4.7 with up to 8 web searches and high effort. Rough estimate: a few cents to ~$0.25 per school depending on how much the model searches and reasons. For all 17 schools budget a few dollars.
