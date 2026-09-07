<script>
  import { onMount } from 'svelte';
  import api from '../../lib/api.js';
  import { toasts } from '../../lib/toast.js';
  import { initials, escapeHtml } from '../../lib/utils.js';
  import { t } from '../../core/i18n/index.js';

  let items = [];
  let loading = true;

  onMount(async () => {
    try {
      items = await api.get('/stats/leaderboard', { limit: 50 });
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  });
</script>

<div class="page">
  <header class="page-header">
    <h1>{$t('leaderboard.title')}</h1>
    <p>{$t('leaderboard.subtitle')}</p>
  </header>

  {#if loading}
    <div class="empty-state"><div class="spinner"></div><p>{$t('leaderboard.loading')}</p></div>
  {:else if items.length === 0}
    <div class="empty-state">
      <h3>{$t('leaderboard.empty.title')}</h3>
      <p>{$t('leaderboard.empty.desc')}</p>
    </div>
  {:else}
    <div class="podium">
      {#each items.slice(0, 3) as u}
        <div class="podium-card podium-card--{u.rank}">
          <div class="podium-card__rank">{u.rank}</div>
          <div class="avatar avatar--lg avatar--gradient podium-card__avatar">{initials(u.username)}</div>
          <div class="podium-card__name">{u.username}</div>
          <div class="podium-card__rating">
            <strong>{u.rating}</strong>
            {$t('leaderboard.points')}
          </div>
        </div>
      {/each}
    </div>

    <div class="table">
      <div class="row row--head">
        <div>#</div>
        <div>{$t('leaderboard.col.user')}</div>
        <div>{$t('leaderboard.col.rating')}</div>
        <div>{$t('leaderboard.col.solved')}</div>
        <div>{$t('leaderboard.col.attempts')}</div>
      </div>
      {#each items as u}
        <div class="row">
          <div class="rank {u.rank <= 3 ? 'rank--top' : ''}">#{u.rank}</div>
          <div class="user">
            <div class="avatar avatar--sm {u.rank <= 3 ? 'avatar--gradient' : ''}">{initials(u.username)}</div>
            {u.username}
          </div>
          <div class="rating">{u.rating}</div>
          <div class="num">{u.solved_count}</div>
          <div class="num">{u.attempt_count || 0}</div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .podium {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: var(--sp-4); margin-bottom: var(--sp-8); align-items: end;
  }
  .podium-card {
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-xl); padding: var(--sp-5); text-align: center;
    position: relative;
  }
  .podium-card--1 {
    order: 2; background: linear-gradient(180deg, var(--brand-soft) 0%, var(--bg-surface) 100%);
    border-color: rgba(91, 140, 255, 0.3);
    padding: var(--sp-6) var(--sp-5); transform: translateY(-12px);
  }
  .podium-card--2 { order: 1; }
  .podium-card--3 { order: 3; }
  .podium-card__rank {
    position: absolute; top: -16px; left: 50%; transform: translateX(-50%);
    background: var(--bg-elevated); border: 1px solid var(--line-2);
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; color: var(--text-1);
  }
  .podium-card--1 .podium-card__rank {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    border: none; color: #1a1300;
  }
  .podium-card__avatar { margin: var(--sp-3) auto var(--sp-2); }
  .podium-card__name { font-weight: 600; font-size: var(--fs-md); margin-bottom: var(--sp-1); }
  .podium-card__rating { font-size: var(--fs-xs); color: var(--text-3); }
  .podium-card__rating strong {
    display: block; font-size: var(--fs-2xl); color: var(--text-1);
    font-weight: 700; letter-spacing: -0.02em;
  }

  .table { background: var(--bg-surface); border: 1px solid var(--line-1); border-radius: var(--r-lg); overflow: hidden; }
  .row {
    display: grid; grid-template-columns: 60px 1fr 100px 100px 100px;
    align-items: center; gap: var(--sp-3); padding: var(--sp-3) var(--sp-5);
    border-bottom: 1px solid var(--line-1); transition: background var(--ease);
  }
  .row:last-child { border-bottom: none; }
  .row:hover { background: var(--bg-elevated); }
  .row--head { font-size: var(--fs-xs); color: var(--text-3); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 500; background: var(--bg-elevated); cursor: default; }
  .row--head:hover { background: var(--bg-elevated); }
  .rank { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text-3); }
  .rank--top { color: var(--warn); }
  .user { display: flex; align-items: center; gap: var(--sp-3); font-weight: 500; min-width: 0; }
  .rating { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--brand); }
  .num { font-family: 'JetBrains Mono', monospace; color: var(--text-2); }
  @media (max-width: 720px) {
    .podium { grid-template-columns: 1fr; }
    .podium-card--1 { order: 1; transform: none; }
    .podium-card--2 { order: 2; }
    .podium-card--3 { order: 3; }
    .row { grid-template-columns: 50px 1fr 80px; }
    .num:nth-child(4), .num:nth-child(5) { display: none; }
    .row--head > div:nth-child(4), .row--head > div:nth-child(5) { display: none; }
  }
</style>
