<script>
  import { onMount } from 'svelte';
  import api from '../../lib/api.js';
  import { toasts } from '../../lib/toast.js';
  import { formatDate, initials } from '../../lib/utils.js';
  import { t } from '../../core/i18n/index.js';

  let items = [];
  let loading = true;

  onMount(async () => {
    try {
      items = await api.get('/news', { limit: 30 });
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  });
</script>

<div class="page">
  <header class="page-header">
    <h1>{$t('news.title')}</h1>
    <p>{$t('news.subtitle')}</p>
  </header>

  {#if loading}
    <div class="empty-state"><div class="spinner"></div><p>{$t('news.loading')}</p></div>
  {:else if items.length === 0}
    <div class="empty-state">
      <h3>{$t('news.empty.title')}</h3>
      <p>{$t('news.empty.desc')}</p>
    </div>
  {:else}
    <div class="list">
      {#each items as n}
        <article class="news-item">
          <div class="news-item__meta">
            <div class="avatar avatar--xs avatar--gradient">{initials(n.author_username || 'TF')}</div>
            <strong>{n.author_username || $t('news.author')}</strong>
            <span>·</span>
            <span>{formatDate(n.published_at || n.created_at)}</span>
          </div>
          <h2 class="news-item__title">{n.title}</h2>
          <div class="news-item__content">{n.content}</div>
        </article>
      {/each}
    </div>
  {/if}
</div>

<style>
  .list { display: flex; flex-direction: column; gap: var(--sp-5); }
  .news-item { background: var(--bg-surface); border: 1px solid var(--line-1); border-radius: var(--r-xl); padding: var(--sp-6) var(--sp-8); transition: border-color var(--ease); }
  .news-item:hover { border-color: var(--line-2); }
  .news-item__meta { display: flex; align-items: center; gap: var(--sp-3); font-size: var(--fs-xs); color: var(--text-3); margin-bottom: var(--sp-3); }
  .news-item__title { font-size: var(--fs-xl); font-weight: 600; letter-spacing: -0.015em; margin-bottom: var(--sp-3); }
  .news-item__content { color: var(--text-2); font-size: var(--fs-sm); line-height: 1.7; white-space: pre-wrap; }
  @media (max-width: 720px) {
    .news-item { padding: var(--sp-5); }
    .news-item__title { font-size: var(--fs-md); }
  }
</style>
