# Additional College Recommendations — Biology / Bioengineering / Math

Date: 2026-04-19

Based on transcript review and stated interests; supplements the existing 17-school list in `schools.txt`.

## Profile snapshot

- Class of 2027 (current junior)
- Weighted GPA **4.3107** — all A / A+ through sophomore year with one A- (AP US History)
- Strong course rigor: Biology (H), Chemistry (H), Algebra 2 (H), Geometry (H), Micro Econ (H), Exploring CS (CP)
- Junior year: 4 APs — **AP Chemistry, AP Precalculus, AP World History, AP Lang & Composition**
- **SAT: 1470** (Math 760, EBRW 710) — 99th percentile composite; Math is 99th+, EBRW is ~95th
- Stated academic interests: **Biology, Bioengineering, Mathematics**
- Residency: Massachusetts (in-state advantage for UMass)

## Existing list (for reference)

Brown, Columbia, UMass Amherst, UC San Diego, Boston U, Cal Poly SLO, Case Western, CMU, Georgia Tech, Johns Hopkins, NC State, Northeastern, NYU, Tufts, UIUC, Rochester, Wisconsin-Madison.

Good coverage: elite engineering (GT, CMU, JHU, UIUC), research Ivies (Brown, Columbia), strong publics (UCSD, UW-Madison), mid-size privates (BU, Tufts, Rochester), and UMass as an in-state anchor. Weak in: **top-tier BioE specialists**, **elite math-heavy privates**, and **elite publics (UC system beyond UCSD)**.

## Recommended additions

### Reaches — top programs in her interest areas

| School | Why it fits |
|---|---|
| **MIT** | BioE #1 nationally, Math top 3, Building 68 / Koch Institute — strongest quantitative-bio culture in the country |
| **Stanford** | BioE top 3, Math top 5, exceptional research opportunities for undergrads, strong Bay Area biotech pipeline |
| **Duke** | BME consistently top 3 (tied with JHU + GT), strong collaborative culture, Pratt School |
| **Rice** | BME top 10, small undergrad focus (~4k), Houston Medical Center adjacency, residential college system |
| **UC Berkeley** | Bio/Bioengineering/Math all top 10, massive research scale, QB3 institute — intense but unmatched for a public |
| **Cornell** | Bio + BME + math all strong, unique CALS agricultural/biotech programs, top math department |
| **UPenn** | Bioengineering top 10, strong math, high cross-registration with Wharton (biotech entrepreneurship) |
| **Northwestern** | BME top 10, very strong math, excellent academic balance, McCormick School |
| **Caltech** | Tiny (~1000 undergrads), elite bio + math, intense but transformative; worth considering if she wants research-first |

### Targets — strong fit given profile

| School | Why it fits |
|---|---|
| **Vanderbilt** | BME strong (top 20), excellent student support culture, good financial aid |
| **WashU St. Louis** | Biology / pre-med powerhouse, strong math, Beyond Boundaries cross-disciplinary option |
| **UCLA** | Strong bio, access to UCLA Health, big research footprint; slightly easier than Berkeley |
| **UMich Ann Arbor** | Top math, strong BME, strong bio, huge engineering ecosystem |
| **UC Santa Barbara (CCS)** | College of Creative Studies is an undergrad honors college built around early research — great for science-focused students |
| **UC Davis** | Strong bio / biological engineering, less intense than Berkeley/UCLA, #1 in ag biotech |

### Likely / safeties — beyond UMass

| School | Why it fits |
|---|---|
| **Stony Brook** | Strong biology + applied math + BME, affordable, Cold Spring Harbor adjacency |
| **UConn** | Solid bio research, close to home, reliable admit for her profile |
| **Rutgers (New Brunswick)** | Strong bio, big research, reliable backup |
| **Worcester Polytechnic (WPI)** | BME strong, project-based curriculum, close to home; project-first model is distinctive |

## Suggested final list balance

- **Reaches** (~6): mix of MIT/Stanford/Duke + a couple "high" reaches already on list (Columbia, Brown, JHU, CMU)
- **Targets** (~6): Case Western, Rochester, BU, Tufts, GT, plus additions like Vanderbilt or UMich
- **Likelies/safeties** (~3): UMass (in-state), NC State, WPI, Stony Brook

A balanced 12–15 school final list tends to work better than 17+ — faster essays, more tailored fit per application.

## Next steps

If she wants to add any of these to the pipeline:

```bash
# Append chosen additions to schools.txt, then:
python3 research_faculty.py --resume --concurrency 4
```

The refresh workflow will automatically pick them up on the next Monday cron, or she can trigger it manually from the Actions tab.

## SAT context for tier placement

A 1470 composite sits:

- **Above 75th percentile** for most targets on the list (UMass, NC State, UIUC, UW-Madison, Rochester, Northeastern, BU, Case Western, Rochester).
- **Within the 25–75 range** for the high-reach tier on the original list (Brown, Columbia, JHU, CMU, Tufts).
- **Below the 50th percentile** for the super-reaches newly added (MIT, Stanford, Caltech, Duke, Rice, Penn, Cornell, Northwestern) — admitted-student medians are typically 1520–1560. Still admissible, especially with a strong math score and rigor, but retaking could push her into the median range.

**Retake recommendation**: if she wants to keep MIT/Stanford/Ivy-tier reaches realistic, targeting a ~40-point bump on the EBRW section (750+) would put her composite at 1510+ and squarely in the applicant pool. Math is already maxed for practical purposes (a 760 → 800 is not a meaningful admissions signal). Most of these schools superscore, so one more sitting with focus on EBRW is low-risk.

## Caveats

These recommendations are based on the transcript, SAT scores, and stated interests. Final decisions should also consider:
- Extracurriculars and specific research/project experience
- SAT II / AP scores once available
- Cost / financial aid preferences
- Location / size / climate preferences
- Specific professors/labs she wants access to (the faculty report can help here)
