(() => {
  'use strict';

  const startBtn = document.getElementById('start-btn');
  const nextBtn = document.getElementById('next-btn');
  const submitBtn = document.getElementById('submit-btn');
  const responseInput = document.getElementById('response-input');
  const stimulus = document.getElementById('stimulus');
  const prompt = document.getElementById('prompt');
  const currentSpanEl = document.getElementById('current-span');
  const bestSpanEl = document.getElementById('best-span');
  const stepLabel = document.getElementById('step-label');
  const feedback = document.getElementById('feedback');
  const historyBody = document.getElementById('history-body');
  const modeRadios = document.querySelectorAll('input[name="mode"]');
  const responseForm = document.getElementById('response-form');

  const BASE_SPAN = 3;
  const DISPLAY_MS = 900;
  const BLANK_MS = 280;

  let mode = 'forward';
  let sessionActive = false;
  let showingSequence = false;
  let currentSpan = BASE_SPAN;
  let bestSpan = 0;
  let attempt = 0;
  let trial = 0;
  let sequence = [];

  modeRadios.forEach((radio) => {
    radio.addEventListener('change', () => {
      mode = radio.value;
      if (!sessionActive) {
        prompt.textContent = mode === 'forward'
          ? 'Press start to begin forward recall.'
          : 'Press start to begin backward recall.';
      }
    });
  });

  startBtn.addEventListener('click', () => {
    startSession();
  });

  nextBtn.addEventListener('click', () => {
    if (!sessionActive || showingSequence) {
      return;
    }
    beginTrial();
  });

  responseForm.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!sessionActive || showingSequence) {
      return;
    }
    handleResponse();
  });

  function startSession() {
    sessionActive = true;
    showingSequence = false;
    currentSpan = BASE_SPAN;
    bestSpan = 0;
    attempt = 0;
    trial = 0;
    sequence = [];
    historyBody.innerHTML = '';
    feedback.textContent = '';
    responseInput.value = '';
    disableResponse();
    nextBtn.disabled = false;
    prompt.textContent = mode === 'forward'
      ? 'Get ready. Click "Next sequence" to start forward recall.'
      : 'Get ready. Click "Next sequence" to start backward recall.';
    stimulus.textContent = '\u00a0';
    stepLabel.textContent = 'Ready';
    updateStatus();
  }

  function beginTrial() {
    if (!sessionActive) {
      return;
    }
    attempt += 1;
    trial += 1;
    sequence = buildSequence(currentSpan);
    showingSequence = true;
    responseInput.value = '';
    disableResponse();
    nextBtn.disabled = true;
    feedback.textContent = '';
    stepLabel.textContent = 'Memorize';
    prompt.textContent = 'Watch the digits. Focus on their order.';
    showSequence(sequence.slice());
  }

  function buildSequence(length) {
    return Array.from({ length }, () => Math.floor(Math.random() * 10));
  }

  function showSequence(queue) {
    if (queue.length === 0) {
      window.setTimeout(() => {
        showingSequence = false;
        stimulus.textContent = '\u00a0';
        prepareForResponse();
      }, BLANK_MS);
      return;
    }

    const digit = queue.shift();
    stimulus.textContent = String(digit);

    window.setTimeout(() => {
      stimulus.textContent = '\u00a0';
      window.setTimeout(() => showSequence(queue), BLANK_MS);
    }, DISPLAY_MS);
  }

  function prepareForResponse() {
    stepLabel.textContent = 'Recall';
    prompt.textContent = mode === 'forward'
      ? 'Type the digits in the same order.'
      : 'Type the digits in reverse order.';
    enableResponse();
    focusResponse();
  }

  function handleResponse() {
    const typed = responseInput.value.replace(/\s+/g, '');
    if (!typed) {
      feedback.textContent = 'Please enter the digits before submitting.';
      focusResponse();
      return;
    }
    if (!/^\d+$/.test(typed)) {
      feedback.textContent = 'Use digits only (0-9).';
      focusResponse();
      return;
    }

    const expected = mode === 'forward'
      ? sequence.join('')
      : sequence.slice().reverse().join('');

    const attemptNumber = attempt;
    const presented = sequence.join(' ');
    const typedFormatted = typed.split('').join(' ');
    const success = typed === expected;

    appendHistory({ attemptNumber, presented, typed: typedFormatted, success });

    if (success) {
      bestSpan = Math.max(bestSpan, currentSpan);
      feedback.textContent = `Correct! Span will increase to ${currentSpan + 1}.`;
      currentSpan += 1;
      attempt = 0;
      endTrial(true);
      return;
    }

    if (attempt < 2) {
      feedback.textContent = `Not quite. You have one more attempt at span ${currentSpan}.`;
      endTrial(false);
      return;
    }

    feedback.textContent = `Session complete. Highest span recalled: ${bestSpan}.`;
    endTrial(false, true);
  }

  function appendHistory(entry) {
    const row = document.createElement('tr');
    const resultText = entry.success ? 'Correct' : 'Incorrect';

    row.innerHTML = [
      `<td>${trial}</td>`,
      `<td>${currentSpan}</td>`,
      `<td>${entry.attemptNumber}/2</td>`,
      `<td>${entry.presented}</td>`,
      `<td>${entry.typed}</td>`,
      `<td>${resultText}</td>`
    ].join('');

    historyBody.append(row);
    historyBody.scrollTop = historyBody.scrollHeight;
  }

  function endTrial(wasCorrect, finished = false) {
    disableResponse();
    nextBtn.disabled = finished;
    if (!finished) {
      stepLabel.textContent = wasCorrect ? 'Advance' : 'Retry';
      prompt.textContent = 'Click "Next sequence" when ready.';
    } else {
      sessionActive = false;
      nextBtn.disabled = true;
      stepLabel.textContent = 'Finished';
      prompt.textContent = 'Press "Start New Session" to try again.';
    }
    updateStatus();
  }

  function updateStatus() {
    currentSpanEl.textContent = sessionActive ? currentSpan : '-';
    bestSpanEl.textContent = bestSpan;
  }

  function enableResponse() {
    responseInput.disabled = false;
    submitBtn.disabled = false;
  }

  function disableResponse() {
    responseInput.disabled = true;
    submitBtn.disabled = true;
  }

  function focusResponse() {
    try {
      responseInput.focus({ preventScroll: true });
    } catch (error) {
      responseInput.focus();
    }
  }
})();
