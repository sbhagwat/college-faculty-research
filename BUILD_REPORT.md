# Build Report — Faculty Outreach Research Pipeline

Date: 2026-04-19
Author: Claude (Opus 4.7) pair-programming with Siyona

## Goal

Given a list of prospective colleges maintained in the Flamingo college-planning tool, produce a ranked list of notable Biology / biotech faculty at each school that Siyona can reach out to for general-interest research outreach.

## Pipeline overview

```
Flamingo web UI (auth-gated)
        │  [step 1] Claude-in-Chrome MCP tools
        ▼
  schools.txt  (17 schools, one per line)
        │  [step 2] research_faculty.py
        │          (Claude API + web_search server-side tool,
        │           parallel execution, incremental output)
        ▼
  faculty_results.json  ─┬─▶  faculty_results.csv     (spreadsheet)
                         ├─▶  faculty_results.md       (readable)
                         ├─▶  faculty_results.js       (data-as-js)
                         └─▶  report.html              (self-contained webapp)
```

## Step 1 — Extract the school list

**What I used.** The `Claude-in-Chrome` MCP server, which exposes the user's logged-in Chrome session to Claude. Sequence of tool calls:

1. `tabs_context_mcp` — see which tabs were open and the current auth state
2. `navigate` — go to `https://collegewise.myflamingo.ai/applications/schools`
3. `get_page_text` — read the rendered DOM after authentication

**Why Claude-in-Chrome instead of the Flamingo API.** Flamingo has no public API, and the page is behind SSO. Trying to replay the auth cookie in a headless request would be fragile. Chrome extension gives us a real browser session that already passed auth.

**Output.** `schools.txt` with 17 schools. The page groups them as a "Short List" (3) and "Long List" (14); I flattened them.

## Step 2 — Research faculty for each school

**Core idea.** Per school, ask Claude Opus 4.7 to identify 4–8 notable faculty in Biology/biotech-adjacent fields, with research area, notable accomplishments, lab URL, and (if publicly listed) email. Use the API's server-side `web_search` tool so Claude can actually search the live web rather than hallucinate.

**Key API choices** (from the `claude-api` skill guidance, see `shared/live-sources.md`):

| Choice | Value | Why |
|---|---|---|
| Model | `claude-opus-4-7` | Default per skill; strongest reasoning for judgment calls like "is this faculty well-known enough" |
| Thinking | `{"type": "adaptive"}` | Opus 4.7 only supports adaptive thinking; the model decides how much to think per step |
| Effort | `output_config: {effort: "high"}` | Favor quality over token cost for one-shot research |
| Tools | `web_search_20260209` (server-side) with `max_uses: 8` | Caps runaway search loops while giving enough room to cross-check multiple faculty |
| Streaming | `client.messages.stream(...).get_final_message()` | Prevents request timeouts on long outputs; per skill default |
| Prompt caching | `cache_control: {"type": "ephemeral"}` on the system prompt | System prompt is identical across 17 calls; caching makes the repeat reads cheaper |
| Max tokens | Raised from 8000 → 24000 | Initial 8000 cap caused silent truncation; web search content + thinking + JSON output needs room |

**Prompt structure.**
- System prompt: role ("research assistant"), quality bar ("well-known leaders — HHMI/NAS/endowed-chair level qualifies"), required fields, and hard rules ("never fabricate emails").
- User prompt: "Find notable Biology/biotech faculty at {school}" + the exact JSON schema to return.

**Output handling.** The model returns a JSON object as text. I parse it with a homegrown extractor that:
1. Strips `json` code fences if the model wraps output in ```` ```json ```` blocks.
2. Uses a character-level brace counter that is string-aware (tracks quote state so braces inside strings don't count toward nesting).
3. Falls back to a JSON sanitizer that escapes literal newlines inside string values — the model sometimes writes multi-line `notable` fields with unescaped `\n`, which is invalid JSON.

When parsing fails, the raw text is preserved under `_raw` so I can debug and retry later rather than losing data.

## Incremental + resumable execution

Two problems to solve:

1. **Large runs shouldn't be atomic.** With 17 schools × ~3 min each, a crash or context window limit mid-run shouldn't discard 12 successful schools. Solution: `write_outputs(results)` is called after every school completes. JSON, CSV, Markdown, JS, and HTML are all written atomically each time.
2. **Resume-friendly.** Added `--resume` (skip schools already in the JSON) and `--retry-failed` (redo anything whose previous attempt has `_raw`, `_error`, or empty `faculty`). This let me kill/restart the script freely without losing progress or needing a separate state file.

## Parallelism

The single-threaded run was dominated by Anthropic+web-search latency (~3–5 min per school). I added a `--concurrency N` flag that dispatches schools through a `ThreadPoolExecutor`. A lock guards the `results` list + `write_outputs` so the incremental writes stay consistent.

Ran the final batch with `--concurrency 4`. Wall-clock dropped roughly 4×.

## Failure modes observed

Out of 17 schools: 12 succeeded, 5 failed to return parseable JSON (Columbia, UMass Amherst, Boston University, Carnegie Mellon, Northeastern, NYU — though BU actually failed twice, once per run).

**Two failure shapes:**

1. **Unescaped newlines in strings.** Model wrote the `notable` field across multiple lines without `\n` escapes. The sanitizer catches most of these, but a few still slipped through when strings also had unescaped quotes or backslashes.
2. **Empty text response.** The message finished with only tool_use blocks and no text content — usually because the model hit `max_tokens` mid-tool-use or produced a very long chain of searches that consumed the budget.

**Mitigations applied:** 3× larger `max_tokens`, smarter JSON extractor, retry-failed flag. These were added mid-run — the 5 remaining failures are queued for a later retry pass with the improved extractor.

## The HTML report

`report_template.html` is a single-page app:

- No build tools — plain HTML + CSS + vanilla JS in one file.
- Loads data via `window.FACULTY_DATA` (set by an inline `<script>` tag).
- Features: live search across name/department/research area/school, per-school filter, three sort modes, badge for parse failures, mailto/lab-site links.

At the end of `write_outputs`, the script renders the template: reads `report_template.html`, replaces `<script src="faculty_results.js"></script>` with an inline `<script>window.FACULTY_DATA = {...}</script>`, and writes the result to `report.html`. That file is fully self-contained — double-click to open, email to someone, paste into a static host.

**Why self-contained over a server.** The dataset is small (~17 schools × ~6 faculty × a few fields = maybe 50 KB). There's no login, no user state, no real-time updates — a static HTML file is the simplest thing that works and deploys anywhere.

## Files produced

| File | Purpose |
|---|---|
| `schools.txt` | Input — edit to add/remove schools |
| `research_faculty.py` | The pipeline |
| `requirements.txt` | Just `anthropic>=0.40.0` |
| `report_template.html` | Static template for the report |
| `faculty_results.json` | Structured data (source of truth) |
| `faculty_results.csv` | Flat table for spreadsheets |
| `faculty_results.md` | Readable markdown version |
| `faculty_results.js` | JS wrapper around the JSON (for future split-file webapp) |
| `report.html` | **Self-contained interactive report — open this.** |
| `run.log` | Last run's stdout |
| `README.md` | How to run |
| `BUILD_REPORT.md` | This file |

## How to update as the school list changes

1. Edit `schools.txt` (add/remove lines).
2. Run `python3 research_faculty.py --resume` — this researches only new schools and preserves existing data.
3. Open `report.html` — it now includes the new schools.

To redo failed schools, add `--retry-failed`.

## Cost notes

Opus 4.7 with adaptive thinking, `high` effort, and up to 8 web searches per school: order-of-magnitude $0.10–0.30 per school. Full run over 17 schools: a couple of dollars including the duplicate parallel launch early in development.

## Things I'd do differently

- Use `client.messages.parse()` with a JSON schema from the start — structured outputs would have caught the unescaped-newline problem at the API layer rather than in my extractor.
- Cap `max_uses` lower (4 instead of 8) — most schools didn't need that many searches, and it reduces the tokens-run-out-mid-response failure mode.
- Add a retry-on-exception wrapper inside `research_school` so transient API hiccups don't require a rerun pass.
