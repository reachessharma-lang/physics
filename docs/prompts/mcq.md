# Prompt: MCQ set

Copy everything in the box below into any AI chat (Claude, ChatGPT, Gemini…).
Fill in the three lines marked ✏️ first.

```
You are writing a multiple-choice question set for "Physics Decoded", a physics study site
for Nepal's NEB curriculum.

✏️ Grade: XII
✏️ Chapter: 15 Alternating Currents
✏️ Topics to cover: rms and peak values; reactance and impedance; LCR series circuit; resonance; power factor

Write 40 questions: about 15 easy, 15 medium and 10 hard. Include numerical problems.

Output ONLY valid JSON, with no commentary and no markdown fences, in exactly this shape:

{
  "title": "<Chapter topic> — <N> MCQs",
  "grade": "XII",
  "chapters": [<chapter number>],
  "date": "<today's date as YYYY-MM-DD>",
  "description": "<one sentence listing the topics covered>",
  "questions": [
    {
      "q": "<question text>",
      "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
      "answer": <index of the correct option: 0 for A, 1 for B, 2 for C, 3 for D>,
      "explanation": "<1–3 sentences explaining why; for numericals show the working>",
      "difficulty": "easy" | "medium" | "hard"
    }
  ]
}

Rules:
- Exactly 4 options per question, all different, with one clearly correct answer.
- Spread the correct answers across positions 0, 1, 2 and 3 roughly evenly.
- Use SI units and Unicode symbols (ω, λ, μ, θ, Δ, ², ³, √, ×, ≈), not LaTeX.
- Do not write "All of the above" or "None of the above".
- Double-check every numerical answer. The explanation must agree with the marked answer.
- Do not use any other fields.
```

Save the answer as `src/lessons/<topic>-mcq.json`, for example `alternating-current-mcq.json`.
If the build reports a problem, paste the error message back to the AI and ask it to fix the JSON.
