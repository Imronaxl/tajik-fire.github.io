import api from '../api.js';
import { escapeHtml, formatDate } from '../utils/helpers.js';

document.addEventListener('DOMContentLoaded', load);

async function load() {
  const wrap = document.getElementById('contests-container');
  try {
    const contests = await api.get('/olympiads/contests', { limit: 30 });
    if (!contests || contests.length === 0) {
      wrap.innerHTML = `
        <div class="empty-state">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"></path></svg>
          <h3>No contests scheduled</h3>
          <p>Check back later or browse the problem archive.</p>
          <a href="/problems" class="btn btn--primary btn--sm mt-4">Go to problems</a>
        </div>`;
      return;
    }
    wrap.innerHTML = `<div class="contest-grid">${contests.map(renderCard).join('')}</div>`;
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state"><h3>Failed to load</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function renderCard(c) {
  const now = Date.now();
  const start = new Date(c.start_time).getTime();
  const end = new Date(c.end_time).getTime();
  const isLive = start <= now && now <= end;
  const isUpcoming = start > now;
  return `
    <article class="contest-card">
      ${isLive ? '<span class="contest-card__live badge badge--success"><span class="live-dot"></span> Live</span>' : ''}
      ${isUpcoming ? `<span class="contest-card__live badge badge--accent">Upcoming</span>` : ''}
      <h3 class="contest-card__title">${escapeHtml(c.title)}</h3>
      <p class="contest-card__desc">${escapeHtml(c.description || 'No description provided.')}</p>
      <div class="contest-card__meta">
        <div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
          ${formatDate(c.start_time)}
        </div>
        <div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          ${formatDate(c.end_time)}
        </div>
      </div>
    </article>`;
}
