<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { toasts } from '../../lib/toast.js';

  let modules = [];
  let loading = true;

  onMount(async () => {
    try {
      modules = await api.get('/learning/modules');
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  });
</script>

<div class="page">
  <header class="page-header">
    <h1>Учебные треки</h1>
    <p>Структурированные пути от основ до продвинутой алгоритмической подготовки. Каждый трек объединяет теорию с graded-задачами.</p>
  </header>

  {#if loading}
    <div class="empty-state"><div class="spinner"></div><p>Загрузка модулей…</p></div>
  {:else if modules.length === 0}
    <div class="empty-state">
      <h3>Модулей пока нет</h3>
      <p>Заглядывайте позже — мы добавляем треки еженедельно.</p>
    </div>
  {:else}
    <div class="grid">
      {#each modules as m}
        <a class="module-card" href={`/learning/${m.slug}`} on:click|preventDefault={() => push(`/learning/${m.slug}`)}>
          <div class="module-card__number">МОДУЛЬ {String(m.order).padStart(2, '0')}</div>
          <h3 class="module-card__title">{m.title}</h3>
          <p class="module-card__desc">{m.description || m.theory_excerpt}</p>
          <div class="module-card__progress"><div class="module-card__progress-bar" style="width:0%"></div></div>
          <div class="text-xs text-3">Открыть модуль</div>
        </a>
      {/each}
    </div>
  {/if}
</div>

<style>
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--sp-5); }
  .module-card {
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-xl); padding: var(--sp-6);
    transition: all var(--ease); position: relative; overflow: hidden;
    text-decoration: none; color: inherit;
    display: flex; flex-direction: column; gap: var(--sp-3);
  }
  .module-card:hover { border-color: var(--line-2); transform: translateY(-2px); }
  .module-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; background: linear-gradient(90deg, var(--brand), var(--purple));
    opacity: 0; transition: opacity var(--ease);
  }
  .module-card:hover::before { opacity: 1; }
  .module-card__number { font-family: 'JetBrains Mono', monospace; font-size: var(--fs-xs); color: var(--text-3); letter-spacing: 0.04em; }
  .module-card__title { font-size: var(--fs-md); font-weight: 600; letter-spacing: -0.01em; }
  .module-card__desc { font-size: var(--fs-sm); color: var(--text-2); line-height: 1.55; flex: 1; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
  .module-card__progress { height: 4px; background: var(--bg-elevated); border-radius: var(--r-full); overflow: hidden; }
  .module-card__progress-bar { height: 100%; background: linear-gradient(90deg, var(--brand), var(--purple)); border-radius: var(--r-full); }
</style>
