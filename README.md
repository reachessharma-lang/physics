# Physics Decoded

Grade XI & XII physics notes and MCQ practice (NEB Curriculum 2076) by Richesh Sharma —
<https://richeshsharma.com.np>

A static website: lesson files go in, a small Python script (`build.py`, standard library only)
turns them into the finished site, and Vercel publishes it automatically on every push.

**Writing content?** Read [docs/AUTHORING.md](docs/AUTHORING.md). Ready-to-paste AI prompts
are in [docs/prompts/](docs/prompts/).

## How it fits together

```
src/
  content.json               site name, links, and the full syllabus of each grade
  lessons/
    <name>.json              an MCQ set: data only
    <name>.html              notes: content-only HTML with a small metadata block on top
  assets/
    css/tokens.css           ALL colours, fonts, radii (light + dark mode)
    css/site.css             layout: header, cards, grade pages, search, footer
    css/lesson.css           notes building blocks + quiz
    js/quiz.js               answering, scoring, filters, saved progress
    js/notes.js              "On this page" highlighting + LaTeX (KaTeX)
    js/search.js             search page
docs/
  AUTHORING.md               how to write lessons
  prompts/                   prompts for any AI to generate content
  examples/example-notes.html  every notes building block (built to /styleguide.html)
build.py                     validates src/ and builds public/
vercel.json                  build settings, Blogger redirects, security + cache headers
public/                      generated site (not committed)
```

The separation is deliberate:

- **Content** (`src/lessons/`) has no styling or scripts, so an AI only has to produce text and data.
- **Design** (`src/assets/css/`) is shared. Change `tokens.css` and every page changes.
- **Behaviour** (`src/assets/js/`) is shared. Improve `quiz.js` once and all MCQ sets improve.
- **Validation** (`build.py`) stops broken files from reaching students. It checks JSON syntax,
  answer indexes, duplicate options, chapter numbers, dates, and banned tags in notes. Full web
  pages (the old Blogger format) are rejected, so every lesson shares one design.

## Common tasks

| Task | How |
|---|---|
| Add a lesson | Add one file to `src/lessons/` ([guide](docs/AUTHORING.md)) |
| Fix a typo in a lesson | Edit the file in `src/lessons/` |
| Change the syllabus / chapter names | Edit `grades` in `src/content.json` |
| Change colours | Edit `src/assets/css/tokens.css` |
| Preview locally | `python build.py` then `python -m http.server 8000 -d public` → <http://localhost:8000> |
| Check files without building | `python build.py --check` |

## Design system

| Token | Light | Dark | Used for |
|---|---|---|---|
| `--brand-600` | `#3949ab` | `#3949ab` | header, hero, footer backgrounds |
| `--brand-ink` | `#3949ab` | `#aab4ff` | indigo text (headings, numbers) |
| `--accent` | `#ffb300` | `#ffb300` | primary button, keyboard focus ring |
| `--notes` | `#1e63d6` | `#7aa7ff` | Notes badges and boxes |
| `--mcq` / `--good` | `#17753a` | `#5fd08a` | MCQ badges, correct answers, tips |
| `--video` / `--bad` | `#b3261e` | `#ff8a80` | video links, wrong answers, warnings |
| `--warn` | `#8a5300` | `#ffc86b` | worked examples, "medium" difficulty |

System font stack (Segoe UI / Roboto / San Francisco), with no web-font downloads. Dark mode
follows the device setting. Every text/background pair meets WCAG AA contrast (4.5:1).

### Accessibility and quality checks (last run 2026-09-24)

axe-core (WCAG 2.0/2.1 A + AA) was run on the home, grade, search, MCQ, notes (styleguide) and
404 pages, in light and dark mode, with quiz answers shown: **0 violations**. Pages have a
skip link, a visible focus ring, labelled search fields, keyboard-operable quiz buttons,
reduced-motion support, and no horizontal scrolling at 375px width.

All notes now use the shared design (the 12 Blogger-era pages were converted on 2026-10-06).
On 2026-10-06 every page was loaded at 360px width with the production Content-Security-Policy:
no horizontal scrolling, no broken images, no blocked resources, and all maths rendered.

### Security and performance

- **Content-Security-Policy** (`vercel.json`): scripts only from this site and `cdn.jsdelivr.net`
  (KaTeX), no plugins, no framing by other sites. Pages contain no inline scripts.
- **Subresource Integrity**: KaTeX is pinned to 0.16.11 and loaded with SRI hashes (`notes.js`),
  so a tampered CDN file is refused by the browser.
- **Caching**: CSS/JS links carry a content hash (`?v=…`, added by `build.py`), so they are cached
  for a year and still update instantly when changed.
- **robots.txt** blocks AI-training crawlers (GPTBot, CCBot, ClaudeBot, …) while search engines
  stay allowed; every page carries a © notice.

## Hosting on Vercel (moving from Blogger)

`vercel.json` already contains the build settings, so no extra configuration is needed:

1. On [vercel.com](https://vercel.com) → **Add New… → Project** → import this GitHub repository.
   Leave every setting at its default (Vercel reads `vercel.json`) and deploy.
2. Check the `*.vercel.app` preview address.
3. **Settings → Domains** → add `richeshsharma.com.np` (and `www.`). Vercel shows the DNS
   records to set at the domain registrar. They replace the records that currently point to Blogger.
4. Once the domain works on Vercel, submit `https://richeshsharma.com.np/sitemap.xml` in
   Google Search Console.

Old Blogger links keep working through redirects in `vercel.json`:

| Old Blogger URL | Goes to |
|---|---|
| `/2026/01/<slug>.html` | `/posts/<slug>.html` |
| `/p/grade-xi.html` | `/pages/grade-xi.html` |
| `/search/label/Wave-Motion-MCQ` | `/search.html?q=Wave-Motion-MCQ` |
| `/search?q=…` | `/search.html?q=…` |
| `/<slug>.html` (old root copies) | `/posts/<slug>.html` |

Every push to `main` redeploys the site. If a lesson file has an error, that lesson is **skipped**
(the Vercel build log lists it under `WARNING`) and every other lesson is still published, so one
bad upload can't freeze the site. The GitHub check (`.github/workflows/check.yml`) runs
`python build.py --strict`, which fails on any problem, so errors still show up as a red ✗ on GitHub.

## Known content issues

- **Full web pages are skipped.** A lesson uploaded as a complete web page (`<!DOCTYPE html>`,
  Tailwind, `<style>`/`<script>`) is left off the site. Until 2026-10-07 such a file stopped the whole
  build, which froze the live site from 2026-10-02 while 16 lessons were uploaded that way; they were
  converted on 2026-10-07. Use the prompts in `docs/prompts/` so lessons come out content-only.
- MCQ options are shown in a fixed shuffled order (`shuffled_options` in `build.py`), because most
  sets stored the correct answer as option A. Questions with options like "None of these" keep
  their order.
- Equations must use `\( … \)` and `\[ … \]`. `$…$` is not rendered (converted pages were rewritten).
- The interactive simulators and calculators in the uploaded pages (photoelectric tube, AC
  generator, cathode-ray beam, standing waves, ray tracer, work/collision calculators) were removed,
  because notes cannot contain scripts. The original pages are in git history (commit `0ff021b`) if
  they are rebuilt later as shared site components.
- Their quizzes became MCQ sets: `electromagnetic-induction-quiz-mcq.json`, `magnetism-quiz-mcq.json`,
  `pipes-strings-quiz-mcq.json`, `refraction-quiz-mcq.json`, `work-energy-and-power-quiz-mcq.json`.
- `photon.html` was an earlier upload of `photons.html` and was removed (its address redirects).
- Diagrams with fixed colours sit on a light panel (`<svg class="panel">`) so they stay readable in
  dark mode. New diagrams should use `currentColor` instead.
- `thermoelectric-effect-mcq.json` question 12 originally had only one option. Three wrong unit
  options were added (A/K, W·m, Ω/K), so please review.

## Roadmap

1. Review the 12 converted notes pages (2026-10-06) side by side with the old versions, and
   tidy box labels or diagrams where needed.
2. MCQ sets for Grade XI chapters 9–13, then the remaining chapters of both grades.
3. Keep all images in `src/assets/img/` (no lesson links to external images any more).
4. Optional later: link YouTube videos per chapter (a `video` field in `content.json`), a "practice
   test" page that mixes questions from several chapters, and Vercel Web Analytics.
