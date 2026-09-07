import api from '../api.js';
import { $, $$, escapeHtml, initials, relativeTime, verdictClass, verdictLabel, languageLabel } from '../utils/helpers.js';

const state = { verdict: '' };

document.addEventListener('DOMContentLoaded', () => {
  bindFilters();
  load();
});

function bindFilters() {
  $$('.pill[data-verdict]').forEach((pill) => {
    pill.addEventListener('click', () => {
      $$('.pill[data-verdict]').forEach((p) => p.classList.remove('active'));
      pill.classList.add('active');
      state.verdict = pill.dataset.verdict;
      load();
    });
  });
}

async function load() {
  const body = document.getElementById('submissions-body');
  try {
    const items = await api.get('/stats/feed', { limit: 100 });
    const filtered = state.verdict ? (items || []).filter((i) => i.verdict === state.verdict) : (items || []);

    if (filtered.length === 0) {
      body.innerHTML = `
        <div class="empty-state">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
          <h3>No submissions found</h3>
          <p>${state.verdict ? 'Try a different filter.' : 'Be the first to submit a solution.'}</p>
        </div>`;
      return;
    }

    body.innerHTML = filtered.map((entry) => `
      <div class="submissions-row">
        <div class="submissions-row__id">#${entry.submission_id}</div>
        <div class="submissions-row__user">
          <div class="avatar avatar--xs avatar--gradient">${escapeHtml(initials(entry.username))}</div>
          ${escapeHtml(entry.username)}
        </div>
        <div class="submissions-row__problem">
          <a href="/problems/${entry.problem_id}">${escapeHtml(entry.problem_title)}</a>
        </div>
        <div><span class="lang-badge">${languageLabel(entry.language)}</span></div>
        <div><span class="${verdictClass(entry.verdict)}">${verdictLabel(entry.verdict)}</span></div>
        <div class="submissions-row__time">${entry.execution_time ? entry.execution_time + 's' : '—'}</div>
        <div class="submissions-row__when">${relativeTime(new Date(entry.created_at))}</div>
      </div>
    `).join('');
  } catch (err) {
    body.innerHTML = `<div class="empty-state"><h3>Failed to load</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}
