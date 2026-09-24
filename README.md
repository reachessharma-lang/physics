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
    css/lesson-bar.css       site bar for the 12 legacy lesson pages
    js/quiz.js               answering, scoring, filters, saved progress
    js/notes.js              "On this page" highlighting + LaTeX (KaTeX)
    js/search.js             search page
docs/
  AUTHORING.md               how to write lessons
  prompts/                   prompts for any AI to generate content
  examples/example-notes.html  every notes building block (built to /styleguide.html)
build.py                     validates src/ and builds public/
vercel.json                  build settings, Blogger redirects, headers
public/                      generated site (not committed)
```

The separation is deliberate:

- **Content** (`src/lessons/`) has no styling or scripts, so an AI only has to produce text and data.
- **Design** (`src/assets/css/`) is shared. Change `tokens.css` and every page changes.
- **Behaviour** (`src/assets/js/`) is shared. Improve `quiz.js` once and all MCQ sets improve.
- **Validation** (`build.py`) stops broken files from reaching students. It checks JSON syntax,
  answer indexes, duplicate options, chapter numbers, dates, and banned tags in notes.

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

The 12 legacy notes pages are not covered. Five of them fail contrast checks because of their
own hard-coded colours (`ideal-gas`, `rate-of-flow-of-heat`, `quantity-of-heat`,
`periodic-motion`, `rotational-dynamics`). Rewriting them in the new format fixes this.

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

Every push to `main` redeploys the site. If a lesson file has an error, the build fails and
the previous version stays online. The same check also runs on GitHub for every pull request
(`.github/workflows/check.yml`).

## Known content issues

- `src/lessons/wave-motion-2.html` is **truncated**. It stops partway through the stationary-waves
  SVG diagram. The rest must be pasted in again from the original.
- `src/lessons/rotational-dynamics.html` loads 5 images from `image.qwenlm.ai`. Download them into
  `src/assets/img/` so they can't disappear.
- `heat-and-temperature` and `thermal-expansion` load `plotly-latest` (frozen at v1.58).
- `thermoelectric-effect.json` question 12 originally had only one option. Three wrong unit
  options were added (A/K, W·m, Ω/K), so please review.
- Grade XI has notes for chapters 9–13 only, and no MCQ sets yet.

## Roadmap

1. Rewrite the 12 legacy notes in the new format (start with the five that fail contrast checks).
2. MCQ sets for Grade XI chapters 9–13, then the remaining chapters of both grades.
3. Download all external images into `src/assets/img/`.
4. Optional later: link YouTube videos per chapter (a `video` field in `content.json`), a "practice
   test" page that mixes questions from several chapters, and Vercel Web Analytics.
