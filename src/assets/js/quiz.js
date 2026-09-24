// Interactive MCQ quiz. The questions are already in the page HTML (rendered by build.py);
// this script only adds answering, scoring, filtering, shuffling and remembering progress.
(function () {
  const quiz = document.querySelector('.quiz');
  if (!quiz) return;

  const list = quiz.querySelector('.questions');
  const items = [...list.querySelectorAll('.question')];
  const scoreEl = quiz.querySelector('.score');
  const bar = quiz.querySelector('.progress span');
  const filter = quiz.querySelector('[data-filter]');
  const result = quiz.querySelector('.result');
  const key = 'pd-quiz:' + quiz.dataset.quiz;

  // state[i] = index of the chosen option, or undefined
  let state = {};
  try { state = JSON.parse(localStorage.getItem(key)) || {}; } catch (e) { state = {}; }
  const save = () => { try { localStorage.setItem(key, JSON.stringify(state)); } catch (e) { /* private mode */ } };

  function show(li, chosen) {
    const answer = +li.dataset.answer;
    const buttons = li.querySelectorAll('.option');
    buttons.forEach((b, i) => {
      b.disabled = chosen !== undefined;
      b.classList.toggle('correct', chosen !== undefined && i === answer);
      b.classList.toggle('wrong', chosen !== undefined && i === chosen && i !== answer);
      b.setAttribute('aria-pressed', i === chosen);
    });
    const exp = li.querySelector('.explanation');
    const verdict = exp.querySelector('.verdict');
    if (chosen === undefined) { exp.hidden = true; return; }
    const right = chosen === answer;
    verdict.textContent = right ? '✓ Correct.' : `✗ Incorrect — answer is ${'ABCDEFGH'[answer]}.`;
    verdict.className = 'verdict ' + (right ? 'good' : 'bad');
    exp.hidden = false;
  }

  function update() {
    const answered = Object.keys(state).length;
    const correct = items.filter(li => state[li.dataset.i] === +li.dataset.answer).length;
    scoreEl.textContent = `${correct} correct · ${answered}/${items.length} answered`;
    bar.style.width = (100 * answered / items.length) + '%';
    const done = answered === items.length;
    result.hidden = !done;
    if (done) {
      result.querySelector('.big').textContent = `${correct} / ${items.length}`;
      result.querySelector('.msg').textContent = correct / items.length >= 0.8 ? 'Excellent work!'
        : correct / items.length >= 0.5 ? 'Good effort — review the ones you missed.' : 'Keep practising — read the explanations and try again.';
    }
    applyFilter();
  }

  function applyFilter() {
    const f = filter.value;
    items.forEach(li => {
      const chosen = state[li.dataset.i];
      li.hidden = !(f === 'all'
        || (f === 'unanswered' && chosen === undefined)
        || (f === 'wrong' && chosen !== undefined && chosen !== +li.dataset.answer)
        || f === li.dataset.difficulty);
    });
  }

  list.addEventListener('click', e => {
    const btn = e.target.closest('.option');
    if (!btn || btn.disabled) return;
    const li = btn.closest('.question');
    const chosen = [...li.querySelectorAll('.option')].indexOf(btn);
    state[li.dataset.i] = chosen;
    save();
    show(li, chosen);
    update();
  });

  filter.addEventListener('change', applyFilter);

  quiz.querySelector('[data-action="reset"]').addEventListener('click', () => {
    if (Object.keys(state).length && !confirm('Clear all your answers for this quiz?')) return;
    state = {};
    save();
    items.forEach(li => show(li, undefined));
    update();
  });

  quiz.querySelector('[data-action="shuffle"]').addEventListener('click', () => {
    const order = items.slice().sort(() => Math.random() - 0.5);
    order.forEach((li, n) => { li.querySelector('.q-num').textContent = (n + 1) + '.'; list.appendChild(li); });
  });

  items.forEach(li => show(li, state[li.dataset.i]));
  update();
})();
