import api from '../api.js';
import { escapeHtml, initials } from '../utils/helpers.js';

document.addEventListener('DOMContentLoaded', load);

async function load() {
  const body = document.getElementById('leaderboard-body');
  const podium = document.getElementById('podium');
  try {
    const items = await api.get('/stats/leaderboard', { limit: 50 });
    if (!items || items.length === 0) {
      body.innerHTML = `
        <div class="empty-state">
          <h3>No ranked developers yet</h3>
          <p>Solve a problem to appear here.</p>
        </div>`;
      podium.innerHTML = '';
      return;
    }

    const top3 = items.slice(0, 3);
    podium.innerHTML = top3.map((u) => `
      <div class="podium-card podium-card--${u.rank}">
        <div class="podium-card__rank">${u.rank}</div>
        <div class="avatar avatar--lg avatar--gradient podium-card__avatar">${escapeHtml(initials(u.username))}</div>
        <div class="podium-card__name">${escapeHtml(u.username)}</div>
        <div class="podium-card__rating">
          <strong>${u.rating}</strong>
          rating points
        </div>
      </div>
    `).join('');

    body.innerHTML = items.map((u) => `
      <div class="leaderboard-row">
        <div class="leaderboard-row__rank ${u.rank <= 3 ? 'leaderboard-row__rank--top' : ''}">#${u.rank}</div>
        <div class="leaderboard-row__user">
          <div class="avatar avatar--sm ${u.rank <= 3 ? 'avatar--gradient' : ''}">${escapeHtml(initials(u.username))}</div>
          ${escapeHtml(u.username)}
        </div>
        <div class="leaderboard-row__rating">${u.rating}</div>
        <div class="leaderboard-row__num">${u.solved_count}</div>
        <div class="leaderboard-row__num">${u.attempt_count || 0}</div>
      </div>
    `).join('');
  } catch (err) {
    body.innerHTML = `<div class="empty-state"><h3>Failed to load</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}
