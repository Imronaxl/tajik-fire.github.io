<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { toasts } from '../../lib/toast.js';
  import { initials, relativeTime, verdictClass, verdictLabel, languageLabel } from '../../lib/utils.js';
  import { t } from '../../core/i18n/index.js';

  let items = [];
  let loading = true;
  let verdictFilter = '';

  const verdicts = [
    { id: '', label: $t('common.all') },
    { id: 'accepted', label: $t('verdict.accepted') },
    { id: 'wrong_answer', label: $t('verdict.wrongAnswer') },
    { id: 'time_limit_exceeded', label: $t('verdict.tle') },
    { id: 'runtime_error', label: $t('verdict.runtimeError') },
    { id: 'compilation_error', label: $t('verdict.compileError') },
  ];

  onMount(load);

  async function load() {
    loading = true;
    try {
      items = await api.get('/stats/feed', { limit: 100 });
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  }

  $: filtered = verdictFilter ? items.filter((i) => i.verdict === verdictFilter) : items;
</script>

<div class="page">
  <header class="page-header">
    <h1>{$t('submissions.title')}</h1>
    <p>{$t('submissions.subtitle')}</p>
  </header>

  <div class="pills mb-4">
    {#each verdicts as v}
      <button class="pill" class:active={verdictFilter === v.id} on:click={() => (verdictFilter = v.id)}>{v.label}</button>
    {/each}
  </div>

  <div class="table">
    <div class="row row--head">
      <div>#</div>
      <div>{$t('submissions.col.user')}</div>
      <div>{$t('submissions.col.problem')}</div>
      <div>{$t('submissions.col.language')}</div>
      <div>{$t('submissions.col.verdict')}</div>
      <div>{$t('submissions.col.time')}</div>
      <div>{$t('submissions.col.when')}</div>
    </div>
    {#if loading}
      <div class="empty-state"><div class="spinner"></div><p>{$t('common.loading')}</p></div>
    {:else if filtered.length === 0}
      <div class="empty-state">
        <h3>{$t('submissions.empty.title')}</h3>
        <p>{$t('submissions.empty.desc')}</p>
      </div>
    {:else}
      {#each filtered as entry}
        <div class="row">
          <div class="id">#{entry.submission_id}</div>
          <div class="user">
            <div class="avatar avatar--xs avatar--gradient">{initials(entry.username)}</div>
            {entry.username}
          </div>
          <div class="problem">
            <a href={`/problems/${entry.problem_id}`} on:click|preventDefault={() => push(`/problems/${entry.problem_id}`)}>{entry.problem_title}</a>
          </div>
          <div><span class="lang-badge">{languageLabel(entry.language)}</span></div>
          <div><span class={verdictClass(entry.verdict)}>{verdictLabel(entry.verdict, $t)}</span></div>
          <div class="time">{entry.execution_time ? entry.execution_time + 's' : '—'}</div>
          <div class="when">{relativeTime(new Date(entry.created_at))}</div>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .pills { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
  .pill { padding: 5px 10px; font-size: var(--fs-xs); font-weight: 500; border-radius: var(--r-full); background: var(--bg-elevated); color: var(--text-3); border: 1px solid var(--line-1); transition: all var(--ease); }
  .pill:hover { color: var(--text-2); }
  .pill.active { background: var(--bg-surface); color: var(--text-1); border-color: var(--line-2); }

  .table { background: var(--bg-surface); border: 1px solid var(--line-1); border-radius: var(--r-lg); overflow: hidden; }
  .row {
    display: grid; grid-template-columns: 60px 1.4fr 1.6fr 100px 140px 80px 100px;
    align-items: center; gap: var(--sp-3); padding: var(--sp-3) var(--sp-5);
    border-bottom: 1px solid var(--line-1); transition: background var(--ease);
  }
  .row:last-child { border-bottom: none; }
  .row:hover { background: var(--bg-elevated); }
  .row--head { font-size: var(--fs-xs); color: var(--text-3); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 500; background: var(--bg-elevated); }
  .row--head:hover { background: var(--bg-elevated); }
  .id { font-family: 'JetBrains Mono', monospace; color: var(--text-3); }
  .user { display: flex; align-items: center; gap: var(--sp-2); font-weight: 500; font-size: var(--fs-sm); }
  .problem { font-size: var(--fs-sm); color: var(--text-2); }
  .problem a { color: var(--text-1); }
  .problem a:hover { color: var(--brand); }
  .time { font-family: 'JetBrains Mono', monospace; color: var(--text-2); font-size: var(--fs-xs); }
  .when { color: var(--text-3); font-size: var(--fs-xs); }
  .lang-badge { font-family: 'JetBrains Mono', monospace; font-size: var(--fs-xs); font-weight: 500; padding: 2px 6px; background: var(--bg-elevated); border-radius: var(--r-sm); color: var(--text-2); }
  @media (max-width: 920px) {
    .row { grid-template-columns: 40px 1fr 100px; }
    .row > div:nth-child(3), .row > div:nth-child(5), .row > div:nth-child(6), .row > div:nth-child(7) { display: none; }
    .row--head > div:nth-child(3), .row--head > div:nth-child(5), .row--head > div:nth-child(6), .row--head > div:nth-child(7) { display: none; }
  }
</style>
