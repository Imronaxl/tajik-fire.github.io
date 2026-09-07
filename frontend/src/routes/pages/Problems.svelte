<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { toasts } from '../../lib/toast.js';
  import { escapeHtml, difficultyClass, debounce } from '../../lib/utils.js';

  let problems = [];
  let loading = true;
  let search = '';
  let difficulties = new Set(['easy', 'medium', 'hard']);
  let category = null;
  let categories = [];
  let sort = 'id-asc';

  onMount(async () => {
    const params = new URLSearchParams(location.search);
    if (params.get('search')) search = params.get('search');
    if (params.get('category')) category = params.get('category');
    await loadCategories();
    await load();
  });

  async function loadCategories() {
    try {
      categories = await api.get('/problems/categories');
    } catch (_) { }
  }

  async function load() {
    loading = true;
    try {
      const params = { limit: 100 };
      if (search) params.search = search;
      if (category) params.category = category;
      let items = await api.get('/problems/', params);
      items = applySort(filterDiff(items));
      problems = items;
    } catch (err) {
      toasts.error(err.message);
    } finally {
      loading = false;
    }
  }

  function filterDiff(list) {
    return list.filter((p) => difficulties.has((p.difficulty || 'easy').toLowerCase()));
  }

  function applySort(list) {
    const arr = [...list];
    const rank = { easy: 1, medium: 2, hard: 3 };
    switch (sort) {
      case 'id-desc': return arr.sort((a, b) => b.id - a.id);
      case 'solved-desc': return arr.sort((a, b) => (b.solved_count || 0) - (a.solved_count || 0));
      case 'difficulty-asc': return arr.sort((a, b) => (rank[a.difficulty] || 0) - (rank[b.difficulty] || 0));
      case 'difficulty-desc': return arr.sort((a, b) => (rank[b.difficulty] || 0) - (rank[a.difficulty] || 0));
      default: return arr.sort((a, b) => a.id - b.id);
    }
  }

  function toggleDiff(d) {
    if (difficulties.has(d)) {
      if (difficulties.size === 1) return;
      difficulties.delete(d);
    } else {
      difficulties.add(d);
    }
    difficulties = difficulties;
    load();
  }

  function pickCategory(c) {
    category = c || null;
    load();
  }

  function reset() {
    search = '';
    category = null;
    difficulties = new Set(['easy', 'medium', 'hard']);
    sort = 'id-asc';
    load();
  }

  const onSearch = debounce(() => load(), 300);
</script>

<div class="page">
  <header class="page-header">
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <div>
        <h1>Архив задач</h1>
        <p>Решай задачи трёх уровней сложности. Отправляй код на Python, C++ или Java и получай вердикт за секунды.</p>
      </div>
      <span class="badge badge--brand">{problems.length} задач</span>
    </div>
  </header>

  <div class="layout">
    <aside class="sidebar">
      <div class="filter-group">
        <label class="filter-label">Поиск</label>
        <input class="input" type="text" placeholder="Поиск по названию…" bind:value={search} on:input={onSearch}>
      </div>

      <div class="filter-group">
        <label class="filter-label">Сложность</label>
        <div class="pills">
          {#each ['easy', 'medium', 'hard'] as d}
            <button class="pill pill--{d}" class:active={difficulties.has(d)} on:click={() => toggleDiff(d)}>
              {d === 'easy' ? 'Лёгкие' : d === 'medium' ? 'Средние' : 'Сложные'}
            </button>
          {/each}
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">Категория</label>
        <div class="pills">
          <button class="pill" class:active={!category} on:click={() => pickCategory(null)}>Все</button>
          {#each categories as c}
            <button class="pill" class:active={category === c.name} on:click={() => pickCategory(c.name)}>
              {c.name} <span class="text-3">{c.count}</span>
            </button>
          {/each}
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">Сортировка</label>
        <select class="select" bind:value={sort} on:change={load}>
          <option value="id-asc">ID по возрастанию</option>
          <option value="id-desc">ID по убыванию</option>
          <option value="solved-desc">Больше решений</option>
          <option value="difficulty-asc">Сначала лёгкие</option>
          <option value="difficulty-desc">Сначала сложные</option>
        </select>
      </div>

      <button class="btn btn--secondary btn--block btn--sm" on:click={reset}>Сбросить фильтры</button>
    </aside>

    <section class="main">
      {#if loading}
        <div class="empty-state"><div class="spinner"></div><p>Загрузка задач…</p></div>
      {:else if problems.length === 0}
        <div class="empty-state">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <h3>Ничего не найдено</h3>
          <p>Попробуйте изменить фильтры.</p>
        </div>
      {:else}
        <div class="table">
          {#each problems as p}
            <a class="row" href={`/problems/${p.id}`} on:click|preventDefault={() => push(`/problems/${p.id}`)}>
              <div class="row__id">#{p.id}</div>
              <div class="row__main">
                <div class="row__title">{p.title}</div>
                <div class="row__meta">
                  {#if p.category}<span>{p.category}</span>{/if}
                  <span>{p.time_limit}s · {p.memory_limit} MB</span>
                </div>
              </div>
              <div class={difficultyClass(p.difficulty)}>{p.difficulty}</div>
              <div class="row__solved">
                <strong>{p.solved_count}</strong>
                <span>решили</span>
              </div>
            </a>
          {/each}
        </div>
      {/if}
    </section>
  </div>
</div>

<style>
  .layout { display: grid; grid-template-columns: 240px 1fr; gap: var(--sp-6); align-items: start; }
  .sidebar {
    position: sticky; top: calc(var(--navbar-h) + var(--sp-4));
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-lg); padding: var(--sp-4);
    display: flex; flex-direction: column; gap: var(--sp-4);
  }
  .filter-label { display: block; margin-bottom: var(--sp-2); font-size: var(--fs-xs); font-weight: 500; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.05em; }
  .pills { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
  .pill {
    padding: 5px 10px; font-size: var(--fs-xs); font-weight: 500;
    border-radius: var(--r-full); background: var(--bg-elevated);
    color: var(--text-3); border: 1px solid var(--line-1);
    transition: all var(--ease);
  }
  .pill:hover { color: var(--text-2); border-color: var(--line-2); }
  .pill.active { background: var(--bg-surface); color: var(--text-1); border-color: var(--line-2); }
  .pill--easy.active { color: var(--diff-easy); border-color: var(--diff-easy); }
  .pill--medium.active { color: var(--diff-medium); border-color: var(--diff-medium); }
  .pill--hard.active { color: var(--diff-hard); border-color: var(--diff-hard); }
  .table { background: var(--bg-surface); border: 1px solid var(--line-1); border-radius: var(--r-lg); overflow: hidden; }
  .row {
    display: grid; grid-template-columns: 60px 1fr 100px 80px;
    align-items: center; gap: var(--sp-3); padding: var(--sp-4) var(--sp-5);
    border-bottom: 1px solid var(--line-1); transition: background var(--ease); color: inherit;
  }
  .row:last-child { border-bottom: none; }
  .row:hover { background: var(--bg-elevated); }
  .row__id { font-family: 'JetBrains Mono', monospace; font-size: var(--fs-sm); color: var(--text-3); font-weight: 500; }
  .row__title { font-weight: 500; font-size: var(--fs-md); margin-bottom: 2px; }
  .row__meta { font-size: var(--fs-xs); color: var(--text-3); display: flex; gap: var(--sp-3); }
  .row__solved { font-size: var(--fs-xs); color: var(--text-2); text-align: center; }
  .row__solved strong { display: block; font-size: var(--fs-md); color: var(--text-1); font-weight: 600; }
  @media (max-width: 920px) {
    .layout { grid-template-columns: 1fr; }
    .sidebar { position: static; }
    .row { grid-template-columns: 50px 1fr 80px; }
    .row__solved { display: none; }
  }
</style>
