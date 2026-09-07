import api from '../api.js';
import toast from '../components/toast.js';
import {
  $, $$, debounce, escapeHtml, renderMarkdown, formatDate, difficultyClass,
} from '../utils/helpers.js';

const state = {
  search: '',
  difficulties: new Set(['easy', 'medium', 'hard']),
  category: null,
  sort: 'id-asc',
  page: 1,
  pageSize: 20,
  total: 0,
};

document.addEventListener('DOMContentLoaded', () => {
  restoreQuery();
  bindFilters();
  loadCategories();
  load();
});

function restoreQuery() {
  const params = new URLSearchParams(location.search);
  const search = params.get('search');
  if (search) {
    state.search = search;
    const input = document.getElementById('filter-search');
    if (input) input.value = search;
  }
  const cat = params.get('category');
  if (cat) state.category = cat;
}

function bindFilters() {
  const search = document.getElementById('filter-search');
  if (search) {
    search.addEventListener('input', debounce((e) => {
      state.search = e.target.value.trim();
      state.page = 1;
      load();
    }, 300));
  }

  $$('.pill[data-diff]').forEach((pill) => {
    pill.addEventListener('click', () => {
      const diff = pill.dataset.diff;
      if (state.difficulties.has(diff)) {
        if (state.difficulties.size === 1) return;
        state.difficulties.delete(diff);
        pill.classList.remove('active');
      } else {
        state.difficulties.add(diff);
        pill.classList.add('active');
      }
      state.page = 1;
      load();
    });
  });

  const sort = document.getElementById('filter-sort');
  sort?.addEventListener('change', (e) => {
    state.sort = e.target.value;
    load();
  });

  document.getElementById('reset-filters')?.addEventListener('click', () => {
    state.search = '';
    state.category = null;
    state.difficulties = new Set(['easy', 'medium', 'hard']);
    state.sort = 'id-asc';
    state.page = 1;
    document.getElementById('filter-search').value = '';
    $$('.pill[data-diff]').forEach((p) => p.classList.add('active'));
    document.getElementById('filter-sort').value = 'id-asc';
    loadCategories();
    load();
  });
}

async function loadCategories() {
  const wrap = document.getElementById('filter-categories');
  if (!wrap) return;
  try {
    const cats = await api.get('/problems/categories');
    if (cats.length === 0) {
      wrap.innerHTML = '<span class="text-xs text-tertiary">No categories yet</span>';
      return;
    }
    wrap.innerHTML = `
      <button class="pill ${state.category === null ? 'active' : ''}" data-cat="" type="button">All</button>
      ${cats.map((c) => `
        <button class="pill ${state.category === c.name ? 'active' : ''}" data-cat="${escapeHtml(c.name)}" type="button">
          ${escapeHtml(c.name)} <span class="text-tertiary">${c.count}</span>
        </button>
      `).join('')}
    `;
    $$('.pill[data-cat]').forEach((p) => {
      p.addEventListener('click', () => {
        state.category = p.dataset.cat || null;
        state.page = 1;
        loadCategories();
        load();
      });
    });
  } catch (_) {
    wrap.innerHTML = '<span class="text-xs text-tertiary">Failed to load</span>';
  }
}

async function load() {
  const list = document.getElementById('problems-list');
  list.innerHTML = `
    <div class="empty-state">
      <div class="spinner"></div>
      <p>Loading problems…</p>
    </div>`;
  try {
    const params = {
      skip: (state.page - 1) * state.pageSize,
      limit: state.pageSize,
    };
    if (state.search) params.search = state.search;
    if (state.category) params.category = state.category;

    let problems = await api.get('/problems/', params);
    problems = applySort(problems, state.sort);
    problems = filterByDifficulty(problems);

    state.total = problems.length;
    updateCount();

    if (problems.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <h3>No problems found</h3>
          <p>Try adjusting your filters.</p>
        </div>`;
      renderPagination();
      return;
    }

    list.innerHTML = `
      <div class="problems-table__header"></div>
      ${problems.map((p) => `
        <a class="problem-row" href="/problems/${p.id}">
          <div class="problem-row__id">#${p.id}</div>
          <div>
            <div class="problem-row__title">${escapeHtml(p.title)}</div>
            <div class="problem-row__meta">
              ${p.category ? `<span>${escapeHtml(p.category)}</span>` : ''}
              <span>${p.time_limit}s · ${p.memory_limit} MB</span>
            </div>
          </div>
          <div class="${difficultyClass(p.difficulty)}">${escapeHtml(p.difficulty)}</div>
          <div class="problem-row__solved">
            <strong>${p.solved_count}</strong>
            <span>solved</span>
          </div>
          <div></div>
        </a>
      `).join('')}
    `;

    $$('.problem-row').forEach((row) => {
      row.addEventListener('click', (e) => {
        e.preventDefault();
        openProblem(row.href.split('/').pop());
      });
    });

    renderPagination();
  } catch (err) {
    list.innerHTML = `<div class="empty-state"><h3>Failed to load</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function filterByDifficulty(problems) {
  return problems.filter((p) => state.difficulties.has((p.difficulty || 'easy').toLowerCase()));
}

function applySort(problems, sort) {
  const arr = [...problems];
  const diffRank = { easy: 1, medium: 2, hard: 3 };
  switch (sort) {
    case 'id-desc': return arr.sort((a, b) => b.id - a.id);
    case 'solved-desc': return arr.sort((a, b) => (b.solved_count || 0) - (a.solved_count || 0));
    case 'difficulty-asc': return arr.sort((a, b) => (diffRank[a.difficulty] || 0) - (diffRank[b.difficulty] || 0));
    case 'difficulty-desc': return arr.sort((a, b) => (diffRank[b.difficulty] || 0) - (diffRank[a.difficulty] || 0));
    default: return arr.sort((a, b) => a.id - b.id);
  }
}

function updateCount() {
  const badge = document.getElementById('problems-count-badge');
  if (badge) badge.textContent = `${state.total} problem${state.total === 1 ? '' : 's'}`;
}

function renderPagination() {
  const wrap = document.getElementById('pagination');
  if (!wrap) return;
  const pages = Math.ceil(state.total / state.pageSize);
  if (pages <= 1) { wrap.innerHTML = ''; return; }

  const buttons = [];
  buttons.push(`<button ${state.page === 1 ? 'disabled' : ''} data-page="${state.page - 1}">←</button>`);
  for (let i = 1; i <= pages; i++) {
    buttons.push(`<button class="${i === state.page ? 'active' : ''}" data-page="${i}">${i}</button>`);
  }
  buttons.push(`<button ${state.page === pages ? 'disabled' : ''} data-page="${state.page + 1}">→</button>`);
  wrap.innerHTML = buttons.join('');
  $$('#pagination button').forEach((b) => {
    b.addEventListener('click', () => {
      state.page = parseInt(b.dataset.page, 10);
      load();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
}

async function openProblem(id) {
  const modal = document.getElementById('problem-modal');
  const body = document.getElementById('modal-body');
  const title = document.getElementById('modal-title');
  const diff = document.getElementById('modal-difficulty');
  const cat = document.getElementById('modal-category');
  const meta = document.getElementById('modal-meta');
  const submitBtn = document.getElementById('modal-submit-btn');

  title.textContent = 'Loading…';
  diff.innerHTML = '';
  cat.textContent = '';
  meta.textContent = '';
  body.innerHTML = `<div class="empty-state"><div class="spinner"></div></div>`;
  modal.classList.add('modal--open');
  modal.setAttribute('aria-hidden', 'false');

  bindModalClose(modal);

  try {
    const lang = localStorage.getItem('preferred_lang') || 'en';
    const p = await api.get(`/problems/${id}`, { lang });
    title.textContent = p.title;
    diff.innerHTML = `<span class="${difficultyClass(p.difficulty)}">${escapeHtml(p.difficulty)}</span>`;
    cat.textContent = p.category || 'general';
    meta.textContent = `${p.time_limit}s · ${p.memory_limit} MB · ${p.solved_count} solved`;
    submitBtn.href = `/problems/${id}/solve`;

    body.innerHTML = `
      <div class="problem-detail">
        <div class="problem-detail__statement">
          ${renderMarkdown(p.statement || 'No statement available.')}
          ${p.input_format ? `<h3>Input</h3><p>${escapeHtml(p.input_format)}</p>` : ''}
          ${p.output_format ? `<h3>Output</h3><p>${escapeHtml(p.output_format)}</p>` : ''}
          ${p.notes ? `<h3>Notes</h3><p>${escapeHtml(p.notes)}</p>` : ''}
        </div>
        <div class="problem-detail__aside">
          <h4>Sample tests</h4>
          <div id="sample-tests">Loading samples…</div>
        </div>
      </div>`;

    loadSampleTests(id);
  } catch (err) {
    body.innerHTML = `<div class="empty-state"><h3>Could not load problem</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

async function loadSampleTests(id) {
  const wrap = document.getElementById('sample-tests');
  if (!wrap) return;
  try {
    const detail = await api.get(`/problems/${id}`);
    const samples = (detail.test_cases || []).filter((t) => t.is_sample);
    if (samples.length === 0) {
      wrap.innerHTML = '<p class="text-tertiary text-xs">No sample tests published.</p>';
      return;
    }
    wrap.innerHTML = samples.map((t, idx) => `
      <div class="test-case">
        <div class="test-case__header"><span>Test ${idx + 1}</span></div>
        <div class="mb-2"><strong class="text-xs text-tertiary">Input</strong><pre>${escapeHtml(t.input_data)}</pre></div>
        <div><strong class="text-xs text-tertiary">Output</strong><pre>${escapeHtml(t.expected_output)}</pre></div>
      </div>
    `).join('');
  } catch (_) {
    wrap.innerHTML = '<p class="text-tertiary text-xs">Failed to load tests.</p>';
  }
}

function bindModalClose(modal) {
  modal.querySelectorAll('[data-modal-close]').forEach((el) => {
    el.addEventListener('click', () => closeModal(modal));
  });
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape') {
      closeModal(modal);
      document.removeEventListener('keydown', esc);
    }
  });
}

function closeModal(modal) {
  modal.classList.remove('modal--open');
  modal.setAttribute('aria-hidden', 'true');
}
