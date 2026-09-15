# Course Page Migration Notes (old site → 2026 site)

Notes for reproducing the migration of legacy course pages (e.g. `/courses/250/24/`)
into the new-style site under `/2026/courses/<num>/<yr>/`. The MATH 250 Fall 2024
migration is the reference implementation — read those files alongside these notes.

## Goal and structure

- Mirror the old file structure exactly: `courses/250/24/index.html` →
  `2026/courses/250/24/index.html`. Old URLs map 1:1 and sibling pages
  (syllabus, letters, calendar, project, notes, helpfulinfo) live in the same folder.
- Every page uses the shared stylesheet via `../../../styles.css` — no per-course
  stylesheet. Course identity is carried by CSS variables in each page's `<style>` block.
- Assets (Mathematica notebooks in `mma/`, PDFs) are NOT copied. Links to them are
  rewritten to root-relative paths pointing at the old location:
  `href="mma/x.nb"` → `href="/courses/250/24/mma/x.nb"`.

## Page template anatomy (see 2026/courses/250/24/index.html)

Top to bottom inside `<body>`:
1. Site nav `#main-nav` with `../../../` links; **Education** is the active item.
2. `.page-grid` > `main.main-column`:
   - `.course-tag` — "MATH 250 • Fall 2024", first thing on the page, compact.
   - `.course-nav` — course sub-nav bar directly below the tag
     (Home • Syllabus • Letters • Calendar • Projects • Content), current page
     marked with `class="here"` (renders as a black pill with white bold text).
     helpfulinfo.html is not in the bar (matches old site); its "here" falls on Home.
   - `.hero-section` — the page h1 (course name on index, page name on subpages).
   - One or more `<section class="section-block"><div class="text-side course-content">`
     blocks holding the content.
3. `aside.sidebar` — "Course Links" widget (sticky): emoji links to the six course
   pages + Discord + Mathematica Online, then a `mailto:chanusa@qc.cuny.edu` button
   labeled "Contact Prof. Hanusa". Hidden under 1000px (`.sidebar { display:none }`)
   because the sub-nav bar covers navigation on mobile.
4. Standard site footer.

## Course color coding

Each course has a color identity taken from the OLD site's `css/demo.css`:
look up `.course_head_title_<num>` (bright shade) and `.course_head_suptitle_<num>`
(dark shade). For MATH 250: bright `#C66`, dark `#A33`.

Each page's `<style>` defines:
```css
body {
    --primary-color: #A33;      /* dark shade: links, bullets, tag, accents  */
    --course-bright: #C66;      /* bright shade: sub-nav bar background      */
    --course-faded: #d99;       /* lighter still: visited links              */
    background-color: #faf4f4;  /* page bg tinted toward the course color    */
}
```
Plus hardcoded derivatives to keep in sync when porting to another course:
- `.btn:hover { background-color: #822; }` (darker shade — overrides the site's blue)
- `.widget-header { border-bottom-color: var(--primary-color); }`
- Sub-nav: `background: var(--course-bright)`, black link text, white on hover,
  `.here` = black pill. Content links: `.section-block a { color: var(--primary-color) }`,
  `.section-block a:visited { color: var(--course-faded) }`.
- The site nav's blue "Education" highlight is inline-styled and intentionally stays blue.

## Content conversion pipeline (per old page)

Extract and transform the old page's `<div class="course_main_<num>">` contents:

1. **Extract**: content = between `<div class="course_main_NNN">` and
   `<div class="footer_wrap">`.
2. **Strip HTML comments browser-style**: repeatedly delete from `<!--` through the
   next `-->` (to EOF if none). CRITICAL — old pages contain broken comments:
   a comment "closed" with `-- >` (space, invalid) and comments never closed at all.
   These silently swallow content and section boundaries if left in. Old pages also
   use comments to hide unreleased/hidden content (e.g. helpfulinfo's "First steps"
   section is fully commented out — the rendered old page is the source of truth).
3. **Strip trailers**: trailing `<p>&nbsp;</p>` spacers and leftover wrapper closes
   `</div> <!-- End course_main-->` / `<!-- End middle -->`.
4. **Rewrite links** (href/src), in this order:
   - external (`http`, `#`, `mailto`) → unchanged
   - sibling course pages (index/syllabus/letters/calendar/project/notes/helpfulinfo
     .html, with anchors) → unchanged (relative)
   - `../../../X` → `/X` (old site root: /schedule/…, /mathematica/…)
   - `../../X` → `/courses/X`
   - anything else local → `/courses/<num>/<yr>/<path>` (assets stay in old dir)
5. **Split into section-blocks**. Split points used per page type:
   - syllabus, helpfulinfo: at each `<h2>`
   - letters: one block per `<div class="course_letter">` (unwrap the div; give the
     section `class="section-block letter"` → red left call-out:
     `.section-block.letter { border-left: 4px solid var(--primary-color); }`)
   - project: at each `<a name="N"></a>` anchor (one block per project); the
     "Skip to" line is pulled OUT of the blocks and becomes a second
     `.course-nav.project-nav` bar below the hero with a white "Skip to:" label
   - notes: at each `<div class="notes_section">`
6. **Balance each block**: walk `<div>`/`</div>`; drop stray closes at depth 0,
   append missing closes at the end. Old content has unclosed divs that otherwise
   break the layout (symptom: the sidebar vanishes or nests inside main).
7. **Wrap** each chunk:
   ```html
   <section class="section-block">
       <div class="text-side course-content">…</div>
   </section>
   ```

### Legacy-content CSS carried on every page
`.course-content` rules for h2/p/ul/li/blockquote spacing, plus ports of old classes:
`.notes_section` (1.5em bold), `.date` (1.25em), `.defn` (bold, indented).
First-child top margins are zeroed so headers don't add space above card padding:
```css
.course-content > :first-child { margin-top: 0; }
.course-content > a[name]:first-child + * { margin-top: 0; }
```
Anchor jumps clear the fixed nav + card padding:
`.course-content a[name] { scroll-margin-top: 120px; }`
Project headings: `<h1 class="project-heading">` — 3em, `var(--primary-color)`.
Index bullet lists use `.resource-list` (1.1em text; bullet ::before has
`font-size:1.2em; top:0; line-height:1.25` so it stays vertically centered —
the 1.25 is (li line-height 1.5) ÷ (bullet font 1.2)).

## Calendar: data-driven (see calendar.html + calendar.json)

The old `<table border bgcolor>` calendar was replaced by `calendar.json` +
a render script in calendar.html:
- JSON: `{ title, semester, weekdays: [Mon..Fri], weeks: [{ week, note?,
  days: [{ date, topic?, class?: true }] }] }`
- Desktop (>700px): semantic table keeping the old look — `<caption>`,
  `<th scope="col">` weekdays, `<th scope="row">` week labels, `#FCC` header band,
  `#C66` class-day cells, `#eee` "other date of note" cells, black text
  (`table.calendar th, td { color: #000 }` — site default text is too low-contrast
  on the red), visible legend, and `.sr-only` "Class meeting:" prefixes so color
  is never the only signal.
- Mobile (≤700px): per-week list, only days with content, red/gray left edge.
- Both views render from the same JSON; uses `fetch()` so preview over http.

## Verification checklist (run after generating each page)

- div balance in `<body>` is 0 (`<div` count == `</div>` count)
- `<!--` count == `-->` count (0/0 after stripping)
- `<aside class="sidebar">` appears AFTER `</main>`
- no remaining relative asset links (everything local is `/courses/...` or a sibling page)
- expected number of `<section class="section-block">` blocks

## Known content notes (MATH 250 F24)

- helpfulinfo's "First steps with Mathematica" section was commented out on the old
  site and is intentionally absent from the new page.
- Week 5 calendar cell was malformed (date inside topic); repaired in calendar.json
  as 02/21 "No class (Monday schedule)".

## MATH 636 (Combinatorics) specifics — migrated Sept 2026

Semesters: 14 (F2014), 15 (F2015), 18 (F2018), 19 (F2019), 22 (S2022).
Colors: dark `#093`, bright `#6d7`, faded `#9ea`, tint `#f4faf5`, btn hover `#062`.
Calendar cell colors differ from the nav colors: week band `#9EA`, class day `#6C7`,
and **exam days `#283`** (dark green, white text) — a third day type (`"exam": true`
in calendar.json, own legend entry + sr-only "Exam:" prefix). 2014/15 have exams;
2018+ used standards-based grading (standards.html) and have none.
Page sets vary: 14/15 = index/syllabus/letters/calendar/notes/project/guidelines;
18 adds standards; 19/22 drop guidelines. Sub-nav follows each year's old menu
(14/15: …Notes Project; 18+: …Standards …Project Content). guidelines.html is
sidebar-only (like helpfulinfo), "here" falls on Home. No discussion-platform links
any year, so sidebars have only course pages + the contact button.
Index pages split at h3 (not h2); the "Welcome to Math 636…" preamble becomes the
hero paragraph; the "This page is for a past course" banner divs are stripped.
Notes pages have ~30 `<div class="date">` lecture entries and no section headers →
kept as a single section-block.
Old-source quirk fixed: a bare `-->` typo in 22's notes (no matching open).

## Reusable script (added during MATH 128 migration)

`2026/courses/migrate_course.py` implements this whole document as a config-driven
tool (run from repo root). Per-course CONFIG: number/name, years+semesters, colors
(incl. calendar band/class/event/exam and `nav_hover`/`skip_label` — needed when the
bright color is light, e.g. yellow, where white hover/label text would vanish),
subnav/sidebar builders, sibling page set, and a page plan with split modes:
`index` (h2/h3, h3→h2 upsized, welcome→hero), `h2`, `h23`, `nsec`, `letters`,
`project` (skip-nav + anchor/h1 normalization), `single`, `calendar`.
Exam days flag from a source bgcolor (`cal_exam_src`) and/or topic prefixes
(`exam_topics`, e.g. "Assess").

## MATH 128 (Mathematical Design) specifics — migrated Sept 2026

Semesters: 20 (F2020), 21 (F2021), 23 (S2023), 24 (S2024).
Colors: dark `#980`, bright `#ff4`, faded `#ba4`, tint `#faf9f0`, btn hover `#760`;
sub-nav hover and skip-label are `#980` (white is invisible on yellow).
Calendar: band `#E9E077`, class `#FF6`, event `#DDDDBB` (old site's tan for
"other dates"); no exams any year (standards-based, assessed in class days only —
no Assess topics found in calendars).
Extra pages: standards.html (all years), terms.html ("Design Terms", split at
notes_section, sidebar-only), makerspace.html (23/24, sidebar-only, "The Makerspace").
2020 has no letters.html. Platforms: 21 Campuswire (generic /c/ link), 23 Discord.
Projects: headings are `<span style="color:#980">` inside notes_section divs
(the heading-span color follows the course, hence the generalized `#\w{3,6}` regex);
2020 = Project 1, 2, Portfolio; 2021 = Projects 1–3; 23/24 = Projects 1–3 + Portfolio.

## MATH 634 (Graph Theory) specifics — migrated Sept 2026

Semesters: 14 (Sp2014), 22 (F2022). Colors: dark `#922`, bright `#fbb` (pink),
faded `#b55`, tint `#fcf5f5`, btn hover `#711`; nav hover/skip label `#922`
(white would vanish on pink). Calendar keeps the old site's `#FCC` band / `#C66`
class cells (they fit the pink theme); exams flagged by "Exam" topic prefix
(Sp2014 Exams 1–2), rendered `#922`.
Extra pages: list.html ("List of Chosen Topics", single block, sub-nav "here" on
Project since project.html links it) and guidelines.html (14 only, sidebar-only).
Sp2014's old menu had a dead homework.html link (file never existed) — omitted.
**Stale-copy rule:** F2022's letters/calendar/guidelines files are byte-identical
copies of Sp2014 (its calendar says "Spring 2014") and were unlinked from the F2022
menu — excluded via the config's `exclude` set. F2022's list.html is also the
Sp2014 copy, but its project page links to it, so it was migrated as-is (flagged
to Chris). When a year's file set looks like another year's, diff before migrating.

## MATH 213 (Math with Mathematica) specifics — migrated Sept 2026

Semesters: 15 (Sp2015), 16 (Sp2016), 17 (**Spring 2018** — directory number does
not match the year; trust the page's own semester text), 18 (F2018), 19 (F2019).
Colors: identical red family to MATH 250 (dark `#A33`, bright `#C66`) — 213 is
250's predecessor. Calendar adds a third cell color: orange `#F96` = project
critique days (2015–Sp2018) — rendered via the exam slot with per-course options
added to the script: `cal_exam_text` (black on orange), `exam_label`
("Critique / key date"), `exam_sr` ("Key date"). Fall semesters have none.
Sp2015 has no letters.html. tutorial1.html (all years, linked from notes) is
sidebar-only ("Tutorial 1", h2 split, "here" on Content).
Sp2015's project2.html/project3.html are superseded drafts unlinked on the old
site — not migrated. 2019's project page has the "skip div swallows the Project 1
heading" malformation (same as 250/24); the script's project mode now handles it
generically: strip `&nbsp;` spacer paragraphs, remove the Skip-to label+links (not
div-bounded), drop emptied notes_section divs, then convert headings.

## Sub-nav rule (Sept 2026)

Content (notes.html — labeled "Content" or "Notes") is ALWAYS the last item in the
course sub-nav bar, for every course and year.

## MATH 141 (Calculus I) specifics — migrated Sept 2026

Semesters: 14 (F2014), 15 (Sp2015), 21 (F2021). Colors: dark `#36c`, bright `#99d`
(periwinkle), faded `#69d`, tint `#f4f6fa`, btn `#249`, nav hover `#36c`.
Calendar: band `#9CE`, class `#39C`, exams `#059` (dark blue cells in 14/15 —
Exams 1–3 each; F2021 is standards-based, none).
homework.html is a real page here ("Book Problems", 19 h3 chapter groups, kept as
a single block with h3 subsection styling; in sub-nav before Content).
`index_h3_top` flag added to the script: 141 indexes use h3 headings with a lone
Office-hours h2 in the middle, all top-level -> split at h2 AND h3, upsizing all
(the two-tier nesting rule would have wrongly nested the resource sections under
Office hours). F2021: Campuswire.

## MATH 142 (Calculus II) specifics — migrated Sept 2026

Semesters: 17 (F2017), 20 (Sp2020). Colors: dark `#079`, bright `#4ad`, faded
`#3ab`, tint `#f0f8fa`, btn/nav-hover `#056`. Calendar: band `#9CE`, class `#4AD`,
no exam cells (standards-based both years). Project = the Goblet Project (h2 split,
no Project-N structure). F2017's old menu had dead letters.html / homework.html
links (files never existed that year) — omitted. Sub-nav preserves each year's own
old menu order (Sp2020 lists Letters right after Home), Content last per the rule.
Notes label: "Daily Topics" (17) / "Content" (20).
Course names come from the old page titles: Calculus I / Calculus II (not the
QC catalog names).

## MATH 201 (Multivariable Calculus) specifics — migrated Sept 2026

Semesters: 14s (Sp2014), 14f (F2014), 15 (F2015), 17 (F2017), 21 (Sp2021) — note
the two 2014 directories use s/f suffixes. Colors: dark `#962`, bright `#fc9`
(peach), faded `#b84`, tint `#fdf8f2`, btn `#741`, nav hover `#962`.
Calendar: band `#FC9`, class `#C73` (rust), exams `#FD5` (yellow, black text —
`cal_exam_text`); Exams 1–3 each semester except Sp2021 (standards-based).
homework.html = "Book Problems" (28 h3 chapter groups, single block) in nav all
years. forum.html (14s/14f/15) = embedded external forum page, migrated as linked
("Forum" in sub-nav) since notes/syllabus/homework content links it — the embed
itself is likely long dead. assessmentdates.html (21) linked from standards/notes,
"here" on Standards, in sidebar. Sp2021: Campuswire.

## MATH 245 (Mathematical Models) specifics — migrated Sept 2026

Ten semesters in two eras; dirs 17=Spring 2018, 19=Fall 2019, 19sp=Spring 2019.
Colors: dark `#629`, bright `#daf` (lavender), faded `#96c`, tint `#f8f4fb`,
btn `#417`, nav hover `#629`.
Calendars differ by era — parsing accepts multiple class colors via the new
`cal_class_src` list (`#b6e` era 1, `#B070FF` era 2); all render in one purple set
(band `#daf`, class `#b6e`); exams `#fbe` pink w/ black text (2014-16 only).
Era 1 (14/15/16, Mathematica era): mathematica.html in nav, with commands.html and
tutorial1.html as its sub-pages ("here" on Mathematica, not in sidebar);
guidelines.html sidebar-only; project pages split at h2 (per-year mode dicts added
to the script: mode can be {year: mode, '*': default}).
Era 2 (17+, Python era): software.html in nav ('single' mode, hero intro);
project mode with anchors — headings run long ("Final Project: Differential
Equation Modeling"), so the heading cap is now 60 chars and skip-nav labels
truncate at ":". abstracts.html (21/22) = student project abstracts in
course_letter markup -> letters mode, "here" on Projects, in sidebar.
Sp2020 splits content across notes01/notes02 ("Course Content (Part 1/2)",
"here" on Content, linked from notes.html).
Sp2018's old menu omitted Letters but its letters file is real (differs from 16) —
kept in nav per the keep-letters preference. 22's index Welcome line is wrapped in
an h3; index mode now drops heading-wrapped Welcome lines (hero carries it).

## MATH 555 (Games and Puzzles) specifics — migrated Sept 2026

One semester: 16 (Spring 2016). Colors: dark `#087`, bright `#4cb` (teal), faded
`#5ba`, tint `#f0faf8`, btn/nav-hover `#065`. Calendar: band `#BBF0E0`, class
`#6CA`, no exams. Minimal page set (index/syllabus/notes/calendar); no letters,
project, or standards. Notes = dated entries with no section markers -> single
block with hero intro. Index uses index_h3_top.

## Migration status

All courses migrated as of Sept 2026: 128, 141, 142, 201, 213, 245, 250, 555,
634, 636 — every course directory under /courses (250/24 remains a phantom,
unreferenced). 250 and 636 predate migrate_course.py (no configs); regenerating
them requires back-porting configs first.

## Consolidation pass (Sept 2026)

- **Shared stylesheet**: all course-page CSS now lives in `2026/courses/course.css`,
  keyed entirely to CSS variables. Each page's inline `<style>` holds only the
  course's variable block (colors + tint) — plus, on project pages, the hero-margin
  overrides. The script's retone() emits the variable block; retone_calendar() now
  handles only legend/JS patches. ~1.3 MB of duplicated CSS removed.
- **250 and 636 back-ported** into migrate_course.py (CONFIG_250 covers 20/21/23
  only — 250/24 stays a phantom and is never regenerated, but its files remain the
  structural templates). All ten courses regenerate from `CONFIGS`.
- Fixes folded in during consolidation: 250/636 notes intros now hero'd (hero_intro
  also peels a leading <p> on single-block pages); bare colored-span project
  headings convert too (Project N / Portfolio / Final Project); `../../schedule/`
  rewrite corrects an old-site typo on three Sp2014 syllabi; 245/19sp syllabus
  content.html -> notes.html; 636/22 stray `-->` is a config content_fix;
  scroll-margin now global (fixes anchor jumps on 245 commands/notes01/notes02).
- CORRECTION to the 636 notes/project entries above: 636 notes have no
  notes_section divs (single block + hero intro), and 636 project pages are
  single-project h2 documents (h2 mode), not Project-N pages.
- 250/24 phantom keeps its full inline CSS (untouched by the consolidation).

## Site-level additions (Sept 2026, beyond courses)

New pages: podcasts.html (15 MathZorro episodes, audio via /podcasts/episodes/,
Apple + RSS subscribe; Stitcher dropped — service shut down), helpfulmma.html
(from mathematica/helpful.html, linked from mathematica.html). A resources.html
page was built then deleted per Chris (not useful enough); its redirect stub
(research/resources.html) points to /2026/education.html instead.
education.html links the course archive.
19 old section URLs (research/*, about/*, courses/index+archive, mathematica/*,
portfolio/, podcasts/) are now meta-refresh stubs targeting **/2026/... paths** —
AT SWITCH-OVER these targets must be updated to root paths (one sed pass).
Old course pages were NOT stubbed (still original).

## Switch-over to root (Sept 15, 2026)

The 2026/ tree now IS the site root. Notes:
- New course pages merged over the old ones in /courses (old asset dirs — mma/,
  notes/, homework/, assessments/ — untouched and still served).
- Redirect stubs' /2026 prefixes stripped. 2026/papers (identical duplicate of
  research/papers, 80MB) was dropped. Drafts moved to /old-drafts.
- migrate_course.py paths are now stale: old course-page SOURCES were overwritten
  in place. To regenerate a course, restore sources from git history first.
- The dead-link audit shows ~many /courses/NNN/YY/notes|homework/*.pdf targets
  that never existed in the repo — those links were dead on the old site too.
