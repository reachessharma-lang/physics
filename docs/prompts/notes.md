# Prompt: Notes

Copy everything in the box below into any AI chat. Fill in the lines marked ✏️ first.
For best results, attach or paste `docs/examples/example-notes.html` as well, as an example of the format.

```
You are writing study notes for "Physics Decoded", a physics study site for Nepal's NEB curriculum.

✏️ Grade: XII
✏️ Chapter: 15 Alternating Currents
✏️ Syllabus topics: rms and peak values; phasors; reactance and impedance; LCR series circuit; resonance; power factor

Write complete, exam-focused notes. Output ONLY the file content (no commentary, no markdown fences),
starting with this metadata block:

---
title: <chapter title>
grade: XII
chapters: [<chapter number>]
date: <today's date as YYYY-MM-DD>
description: <one sentence summary>
---

Then the content as plain HTML fragments. The site provides all styling, so:
- DO NOT write <html>, <head>, <body>, <style>, <script>, <link> or style="..." attributes.
- Use <h2> for each main section (one per syllabus topic) and <h3> for sub-sections.
- Use <p>, <ul>, <ol>, <table>, <strong>, <em> for text.
- Maths in LaTeX: inline \( ... \), display formulas as
  <div class="formula">\[ ... \]<span class="where">where ... </span></div>
- Use these ready-made boxes (and no other classes):
  <div class="box definition">...</div>   a definition
  <div class="box law">...</div>          a law or principle
  <div class="box example">...</div>      a worked numerical example; put the answer inside
                                          <details class="solution"><summary>Show solution</summary>...</details>
  <div class="box tip">...</div>          an exam tip
  <div class="box warning">...</div>      a common mistake
  <div class="box note">...</div>         a side note
  <ul class="key-points">...</ul>         the summary list at the end
  <div class="cols"><div>...</div><div>...</div></div>   a side-by-side comparison
- Diagrams: simple inline <svg viewBox="..."> inside <figure> with a <figcaption>, using
  stroke="currentColor" / fill="none" so they work in dark mode, and role="img" aria-label="...".
  Do not link to images on other websites.

Structure: short introduction → one <h2> per syllabus topic (definitions, derivations step by step,
formulas) → at least 3 worked examples → common mistakes → key points summary.
Check all derivations and numerical answers.
```

Save the answer as `src/lessons/<topic>.html`, for example `alternating-current.html`.
Open `/posts/<topic>.html` after the site rebuilds and read it through before sharing it with students.
