import api from '../api.js';
import auth from '../auth.js';
import toast from '../components/toast.js';
import {
  $, escapeHtml, renderMarkdown, difficultyClass, verdictClass, verdictLabel,
  languageLabel, relativeTime,
} from '../utils/helpers.js';

const STARTER_CODE = {
  python3: `# Read input, solve the problem, write output.\n# Example: a, b = map(int, input().split())\n`,
  cpp17: `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(nullptr);\n\n    return 0;\n}\n`,
  java11: `import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n\n    }\n}\n`,
};

const pathParts = window.location.pathname.split('/').filter(Boolean);
const problemId = pathParts[1] === 'problems' ? parseInt(pathParts[2], 10) : null;

let lastSubmissionId = null;
let pollTimer = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!problemId || Number.isNaN(problemId)) {
    toast.error('Problem not found.');
    setTimeout(() => { window.location.href = '/problems'; }, 800);
    return;
  }

  bindControls();
  await loadProblem();
});

async function loadProblem() {
  try {
    const lang = localStorage.getItem('preferred_lang') || 'en';
    const p = await api.get(`/problems/${problemId}`, { lang });
    $('#editor-title').textContent = p.title;
    $('#editor-difficulty').innerHTML = `<span class="${difficultyClass(p.difficulty)}">${escapeHtml(p.difficulty)}</span>`;
    $('#editor-category').textContent = p.category || 'general';
    $('#editor-meta').textContent = `${p.time_limit}s · ${p.memory_limit} MB`;
    $('#editor-statement').innerHTML = renderMarkdown(p.statement || 'No statement.');
    if (p.input_format) $('#editor-statement').innerHTML += `<h3>Input</h3><p>${escapeHtml(p.input_format)}</p>`;
    if (p.output_format) $('#editor-statement').innerHTML += `<h3>Output</h3><p>${escapeHtml(p.output_format)}</p>`;
    if (p.notes) $('#editor-statement').innerHTML += `<h3>Notes</h3><p>${escapeHtml(p.notes)}</p>`;

    const savedLang = localStorage.getItem('editor_lang') || 'python3';
    $('#editor-lang').value = savedLang;
    loadSavedCode(savedLang);
  } catch (err) {
    $('#editor-statement').innerHTML = `<div class="empty-state"><h3>Failed to load</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function bindControls() {
  $('#editor-lang').addEventListener('change', (e) => {
    localStorage.setItem('editor_lang', e.target.value);
    loadSavedCode(e.target.value);
  });
  $('#editor-reset').addEventListener('click', () => {
    if (!confirm('Reset the editor to the starter template?')) return;
    const lang = $('#editor-lang').value;
    $('#editor-code').value = STARTER_CODE[lang] || '';
    saveCode(lang);
  });
  $('#editor-code').addEventListener('input', () => saveCode($('#editor-lang').value));
  $('#editor-submit').addEventListener('click', submit);
}

function loadSavedCode(lang) {
  const saved = localStorage.getItem(`code:${problemId}:${lang}`);
  $('#editor-code').value = saved || STARTER_CODE[lang] || '';
}

function saveCode(lang) {
  localStorage.setItem(`code:${problemId}:${lang}`, $('#editor-code').value);
}

async function submit() {
  if (!auth.isAuthenticated()) {
    toast.warning('Sign in to submit solutions.');
    setTimeout(() => { window.location.href = `/login?next=/problems/${problemId}/solve`; }, 800);
    return;
  }

  const code = $('#editor-code').value.trim();
  if (!code) {
    toast.warning('Write some code first.');
    return;
  }

  const lang = $('#editor-lang').value;
  const btn = $('#editor-submit');
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner" style="width:14px;height:14px;border-width:2px;"></div> Submitting…';

  try {
    const submission = await api.post('/problems/submissions', {
      problem_id: problemId,
      language: lang,
      code,
    });
    lastSubmissionId = submission.id;
    renderPending(submission);
    pollForVerdict(submission.id);
  } catch (err) {
    toast.error(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> Submit';
  }
}

function renderPending(submission) {
  const results = $('#editor-results');
  results.innerHTML = `
    <div class="verdict-card verdict-card--pending">
      <div class="verdict-card__icon">
        <div class="spinner" style="width:14px;height:14px;border-width:2px;"></div>
      </div>
      <div class="verdict-card__main">
        <div class="verdict-card__title">Submission #${submission.id} · ${languageLabel(submission.language)}</div>
        <div class="verdict-card__meta">Judging…</div>
      </div>
    </div>`;
}

function pollForVerdict(submissionId) {
  if (pollTimer) clearInterval(pollTimer);
  let attempts = 0;
  pollTimer = setInterval(async () => {
    attempts++;
    try {
      const s = await api.get(`/problems/submissions/${submissionId}`);
      if (s.verdict && s.verdict !== 'pending' && s.verdict !== 'judging') {
        clearInterval(pollTimer);
        pollTimer = null;
        renderVerdict(s);
      }
    } catch (_) { }
    if (attempts > 30) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }, 800);
}

function renderVerdict(s) {
  const results = $('#editor-results');
  const isError = !['accepted'].includes(s.verdict);
  const cardClass = s.verdict === 'accepted' ? 'verdict-card--accepted' :
                    s.verdict === 'wrong_answer' ? 'verdict-card--wrong_answer' :
                    'verdict-card--error';

  const icon = s.verdict === 'accepted'
    ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'
    : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

  const existing = results.querySelector('.verdict-card--pending');
  if (existing) existing.remove();

  results.insertAdjacentHTML('afterbegin', `
    <div class="verdict-card ${cardClass}">
      <div class="verdict-card__icon">${icon}</div>
      <div class="verdict-card__main">
        <div class="verdict-card__title">Submission #${s.id} · ${languageLabel(s.language)}</div>
        <div class="verdict-card__meta">
          <span class="${verdictClass(s.verdict)}">${verdictLabel(s.verdict)}</span>
          · ${s.test_passed}/${s.test_total} tests
          ${s.execution_time ? ` · ${s.execution_time}s` : ''}
          ${s.memory_used ? ` · ${s.memory_used} MB` : ''}
          · ${relativeTime(new Date(s.created_at))}
        </div>
        ${s.error_message ? `<div class="verdict-card__error">${escapeHtml(s.error_message)}</div>` : ''}
      </div>
    </div>
  `);

  if (s.verdict === 'accepted') {
    toast.success(`Accepted! ${s.test_passed}/${s.test_total} tests passed.`);
  } else if (isError) {
    toast.error(`${verdictLabel(s.verdict)} on test ${s.test_passed + 1}`);
  }
}
