<script>
  import { onMount } from 'svelte';
  import api from '../../lib/api.js';
  import { toasts } from '../../lib/toast.js';
  import { formatDate } from '../../lib/utils.js';

  let items = [];
  let loading = true;

  onMount(async () => {
    try {
      items = await api.get('/olympiads/contests', { limit: 30 });
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  });
</script>

<div class="page">
  <header class="page-header">
    <h1>Контесты</h1>
    <p>Текущие и предстоящие соревнования. Участвуй, чтобы проверить скорость и точность.</p>
  </header>

  {#if loading}
    <div class="empty-state"><div class="spinner"></div><p>Загрузка контестов…</p></div>
  {:else if items.length === 0}
    <div class="empty-state">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"></path></svg>
      <h3>Контесты не запланированы</h3>
      <p>Заглядывайте позже — мы добавляем соревнования еженедельно.</p>
    </div>
  {:else}
    <div class="grid">
      {#each items as c}
        {@const now = Date.now()}
        {@const start = new Date(c.start_time).getTime()}
        {@const end = new Date(c.end_time).getTime()}
        {@const live = start <= now && now <= end}
        {@const upcoming = start > now}
        <article class="contest-card">
          {#if live}
            <span class="contest-card__live badge badge--ok"><span class="live-dot"></span> Идёт</span>
          {:else if upcoming}
            <span class="contest-card__live badge badge--brand">Скоро</span>
          {/if}
          <h3 class="contest-card__title">{c.title}</h3>
          <p class="contest-card__desc">{c.description || 'Описание отсутствует.'}</p>
          <div class="contest-card__meta">
            <div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
              {formatDate(c.start_time)}
            </div>
            <div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              {formatDate(c.end_time)}
            </div>
          </div>
        </article>
      {/each}
    </div>
  {/if}
</div>

<style>
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--sp-4); }
  .contest-card {
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-lg); padding: var(--sp-5);
    transition: all var(--ease); position: relative; overflow: hidden;
  }
  .contest-card:hover { border-color: var(--line-2); transform: translateY(-2px); }
  .contest-card__live { position: absolute; top: var(--sp-4); right: var(--sp-4); }
  .contest-card__title { font-size: var(--fs-md); font-weight: 600; margin-bottom: var(--sp-2); padding-right: 90px; }
  .contest-card__desc {
    font-size: var(--fs-sm); color: var(--text-2); line-height: 1.5;
    margin-bottom: var(--sp-4); display: -webkit-box;
    -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  }
  .contest-card__meta {
    display: flex; align-items: center; gap: var(--sp-4);
    font-size: var(--fs-xs); color: var(--text-3);
    border-top: 1px solid var(--line-1); padding-top: var(--sp-3);
  }
  .contest-card__meta div { display: flex; align-items: center; gap: var(--sp-1); }
  .live-dot {
    display: inline-block; width: 8px; height: 8px;
    background: var(--ok); border-radius: 50%;
    box-shadow: 0 0 0 4px var(--ok-soft);
    animation: pulse 1.4s infinite;
  }
</style>
