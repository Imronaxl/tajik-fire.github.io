import api from '../api.js';
import { escapeHtml, formatDate, initials } from '../utils/helpers.js';

document.addEventListener('DOMContentLoaded', load);

async function load() {
  const list = document.getElementById('news-list');
  try {
    const items = await api.get('/news', { limit: 30 });
    if (!items || items.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6z"></path></svg>
          <h3>No news yet</h3>
          <p>Updates will appear here when published.</p>
        </div>`;
      return;
    }
    list.innerHTML = items.map((n) => `
      <article class="news-item">
        <div class="news-item__meta">
          <div class="avatar avatar--xs avatar--gradient">${escapeHtml(initials(n.author_username || 'DS'))}</div>
          <strong>${escapeHtml(n.author_username || 'DevStudio team')}</strong>
          <span>·</span>
          <span>${formatDate(n.published_at || n.created_at)}</span>
        </div>
        <h2 class="news-item__title">${escapeHtml(n.title)}</h2>
        <div class="news-item__content">${escapeHtml(n.content)}</div>
      </article>
    `).join('');
  } catch (err) {
    list.innerHTML = `<div class="empty-state"><h3>Failed to load</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}
