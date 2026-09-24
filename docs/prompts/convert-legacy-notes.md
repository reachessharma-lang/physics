# Prompt: Convert an old lesson to the new notes format

The 12 older notes pages (from Blogger) are complete web pages with their own styling.
Use this prompt to turn one into the new content-only format, then **delete** the old file
and save the new one under the **same file name** so its web address doesn't change.

Paste the prompt from [`notes.md`](notes.md), and add this paragraph before it:

```
Below is an existing lesson written as a full HTML page with its own CSS and JavaScript.
Rewrite it into the format described below. Keep ALL the physics content: every definition,
derivation, formula, worked example, table and question. Drop all styling, navigation menus,
scripts, animations and decorative elements. Convert formulas to LaTeX. Redraw simple diagrams
as inline SVG; for complex ones, write <!-- TODO: diagram of ... --> where the diagram should go.
Interactive quizzes at the end of the page should be returned SEPARATELY as an MCQ JSON file
in the format I will describe afterwards.

<paste the old file here>
```

Afterwards compare the old and new pages side by side on the site before deleting the old one.
