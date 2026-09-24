# Writing lessons for Physics Decoded

Every lesson is **one file** in `src/lessons/`. The file name becomes the web address:
`src/lessons/alternating-current.html` → `/posts/alternating-current.html`.

There are two kinds of lesson:

| Kind | File | What goes in it |
|---|---|---|
| **MCQ set** | `<name>.json` | Only data: questions, options, answer, explanation |
| **Notes** | `<name>.html` | Only content: headings, text, formulas and a few ready-made boxes |

Content files contain **no design**: no colours, fonts, `<style>` or `<script>`. The whole site
shares one look, defined in `src/assets/css/`. This means you can ask *any* AI to write
content with the prompts in [`docs/prompts/`](prompts/), and it will look right automatically.

File names: lowercase words joined by hyphens, e.g. `lenses-mcq.json`, `refraction-through-prisms.html`.

---

## Publishing a lesson (on GitHub, no software needed)

1. Open the repository on GitHub → `src/lessons` → **Add file → Create new file**.
2. Name it (e.g. `alternating-current-mcq.json`) and paste the content.
3. Click **Commit changes**. Vercel rebuilds the site within about a minute.
4. If something is wrong in the file, the Vercel build fails. The live site then **stays as
   it was**, and the build log lists every problem in plain English
   (e.g. `question 12: two options are identical`).

To check files on your own computer first, run `python build.py --check`.

---

## MCQ set (`.json`)

```json
{
  "title": "Alternating Current — 40 MCQs",
  "grade": "XII",
  "chapters": [15],
  "date": "2026-10-01",
  "description": "RMS values, reactance, impedance, resonance and power factor.",
  "questions": [
    {
      "q": "The rms value of an alternating current of peak value I₀ is:",
      "options": ["I₀/2", "I₀/√2", "√2 I₀", "2I₀/π"],
      "answer": 1,
      "explanation": "For a sinusoidal current, I_rms = I₀/√2 ≈ 0.707 I₀.",
      "difficulty": "easy"
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Shown on the page and in search |
| `grade` | yes | `"XI"` or `"XII"` |
| `chapters` | yes | Chapter number(s) from the syllabus (see below), e.g. `[15]` or `[7, 8, 9]` |
| `date` | yes | `YYYY-MM-DD`; newest lessons appear first on the home page |
| `description` | no | One sentence shown under the title |
| `questions[].q` | yes | Question text (plain text; use Unicode such as ω, λ, ², √) |
| `questions[].options` | yes | 2–6 different options; 4 is normal |
| `questions[].answer` | yes | **Position of the correct option, counting from 0**: 0 = A, 1 = B, 2 = C, 3 = D |
| `questions[].explanation` | recommended | Shown after the student answers |
| `questions[].difficulty` | recommended | `"easy"`, `"medium"` or `"hard"` |

---

## Notes (`.html`)

Start with a metadata block, then write plain HTML content:

```html
---
title: Alternating Current
grade: XII
chapters: [15]
date: 2026-10-01
description: RMS values, phasors, LCR circuits and resonance.
---

<h2>Introduction</h2>
<p>An alternating current changes direction periodically…</p>
```

Every `<h2>` becomes an entry in the automatic "On this page" menu.

### Building blocks

| You write | You get |
|---|---|
| `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<table>`, `<strong>`, `<em>` | Normal text styling |
| `\( E = mc^2 \)` | Inline formula (LaTeX) |
| `<div class="formula">\[ F = -kx \]<span class="where">where k is…</span></div>` | Centred display formula with an optional "where" line |
| `<div class="box definition">…</div>` | Blue **Definition** box |
| `<div class="box law">…</div>` | Indigo **Law / Principle** box |
| `<div class="box example">…</div>` | Amber **Worked example** box |
| `<div class="box tip">…</div>` | Green **Exam tip** box |
| `<div class="box warning">…</div>` | Red **Common mistake** box |
| `<div class="box note">…</div>` | Grey **Note** box |
| `<div class="box law" data-title="Newton's second law">…</div>` | Any box with a custom label |
| `<details class="solution"><summary>Show solution</summary>…</details>` | Hidden solution the student clicks to open |
| `<ul class="key-points"><li>…</li></ul>` | Tick-mark summary list |
| `<div class="cols"><div>…</div><div>…</div></div>` | Side-by-side comparison |
| `<figure><img src="/assets/img/lens.png" alt="…"><figcaption>…</figcaption></figure>` | Image with caption |
| `<figure><svg viewBox="…">…</svg><figcaption>…</figcaption></figure>` | Inline SVG diagram (use `stroke="currentColor"` so it works in dark mode) |

**Not allowed in notes:** `<style>`, `<script>`, `<link>`, `style="…"`, `<html>/<head>/<body>`.
The build rejects them so that every page keeps the same look.

**See every block in action:** open `/styleguide.html` on the site. Its source is
[`docs/examples/example-notes.html`](examples/example-notes.html), and copying that file is
the fastest way to start new notes.

### Images

Put images in `src/assets/img/` (create the folder the first time) and refer to them as
`/assets/img/<name>.png`. Do **not** link to images hosted on other websites. They
disappear (several old lessons still use `image.qwenlm.ai` links).

---

## Chapter numbers

Chapter numbers come from `src/content.json` (and are shown on the grade pages).

**Grade XI:** 1 Physical Quantities · 2 Vectors · 3 Kinematics · 4 Dynamics · 5 Work, Energy and Power ·
6 Circular Motion · 7 Gravitation · 8 Elasticity · 9 Heat and Temperature · 10 Thermal Expansion ·
11 Quantity of Heat · 12 Rate of Heat Flow · 13 Ideal Gas · 14 Reflection at Curved Mirrors ·
15 Refraction at Plane Surfaces · 16 Refraction through Prisms · 17 Lenses · 18 Dispersion ·
19 Electric Charges · 20 Electric Field · 21 Electric Potential · 22 Capacitor · 23 DC Circuits ·
24 Nuclear Physics · 25 Solids · 26 Recent Trends in Physics

**Grade XII:** 1 Rotational Dynamics · 2 Periodic Motion · 3 Fluid Statics and Dynamics · 4 Wave Motion ·
5 Acoustic Phenomena · 6 Nature and Propagation of Light · 7 Interference · 8 Diffraction ·
9 Polarization · 10 First Law of Thermodynamics · 11 Second Law of Thermodynamics ·
12 Electrical Circuits · 13 Magnetic Field and Properties of Materials · 14 Electromagnetic Induction ·
15 Alternating Currents · 16 Electrons and Photons · 17 Semiconductor Devices ·
18 Atomic and Nuclear Physics · 19 Recent Trends in Physics

---

## Old ("legacy") lessons

Twelve notes pages from the Blogger days are complete stand-alone web pages (they start with
`<!doctype html>` after the metadata block). They still work: the build adds the site bar and
footer. But they don't follow the shared design, and several fail contrast checks. When a
chapter is revised, rewrite it in the new notes format using [`prompts/convert-legacy-notes.md`](prompts/convert-legacy-notes.md),
and delete the old file.
