import api from '../api.js';
import auth from '../auth.js';
import toast from '../components/toast.js';
import { $, $$, escapeHtml, renderMarkdown, difficultyClass } from '../utils/helpers.js';

const pathParts = window.location.pathname.split('/').filter(Boolean);
const moduleSlug = pathParts[1];

document.addEventListener('DOMContentLoaded', () => {
  if (moduleSlug) loadDetail(moduleSlug);
  else loadList();
});

async function loadList() {
  const grid = document.getElementById('learning-grid');
  try {
    const modules = await api.get('/learning/modules');
    if (!modules || modules.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
          <h3>No learning modules yet</h3>
          <p>Check back soon — we're shipping tracks weekly.</p>
        </div>`;
      return;
    }
    grid.innerHTML = modules.map((m) => `
      <a class="module-card" href="/learning/${m.slug}">
        <div class="module-card__number">MODULE ${String(m.order).padStart(2, '0')}</div>
        <h3 class="module-card__title">${escapeHtml(m.title)}</h3>
        <p class="module-card__desc">${escapeHtml(m.description || m.theory_excerpt || '')}</p>
        <div class="module-card__progress"><div class="module-card__progress-bar" style="width:0%"></div></div>
        <div class="text-xs text-tertiary">Click to start learning</div>
      </a>
    `).join('');
  } catch (err) {
    grid.innerHTML = `<div class="empty-state"><p>${escapeHtml(err.message)}</p></div>`;
  }
}

async function loadDetail(slug) {
  const grid = document.getElementById('learning-grid');
  const header = document.querySelector('.page-header');

  if (!auth.isAuthenticated()) {
    toast.warning('Sign in to view full module content.');
    setTimeout(() => { window.location.href = `/login?next=/learning/${slug}`; }, 800);
    return;
  }

  try {
    const m = await api.get(`/learning/modules/${slug}`);
    header.innerHTML = `
      <a href="/learning" class="text-sm text-tertiary flex items-center gap-2 mb-2">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
        Back to modules
      </a>
      <h1>${escapeHtml(m.title)}</h1>
      <p>${escapeHtml(m.description || '')}</p>
    `;
    grid.outerHTML = `
      <div class="module-detail">
        <div class="module-theory">${renderMarkdown(m.theory_content || 'No theory published yet.')}</div>
        <div class="module-problems">
          <h3>Practice problems</h3>
          ${(m.problems || []).map((p) => `
            <a class="module-problem-row" href="/problems/${p.id}">
              <span class="module-problem-row__order">${String(p.order).padStart(2, '0')}</span>
              <span class="module-problem-row__title">${escapeHtml(p.title)}</span>
              <span class="${difficultyClass(p.difficulty)}">${escapeHtml(p.difficulty)}</span>
            </a>
          `).join('') || '<p class="text-tertiary text-sm">No problems linked yet.</p>'}
        </div>
      </div>
    `;
  } catch (err) {
    grid.innerHTML = `<div class="empty-state"><h3>Module not found</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}
