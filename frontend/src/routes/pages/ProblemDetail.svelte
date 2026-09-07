<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { toasts } from '../../lib/toast.js';
  import { renderMarkdown, difficultyClass, escapeHtml } from '../../lib/utils.js';
  import { t } from '../../core/i18n/index.js';

  export let params;

  let problem = null;
  let loading = true;
  let sampleTests = [];

  onMount(async () => {
    try {
      const lang = localStorage.getItem('preferred_lang') || 'en';
      problem = await api.get(`/problems/${params.id}`, { lang });
      const detail = await api.get(`/problems/${params.id}`);
      sampleTests = (detail.test_cases || []).filter((t) => t.is_sample);
    } catch (err) {
      toasts.error(err.message);
    } finally {
      loading = false;
    }
  });

  function solve() {
    push(`/problems/${params.id}/solve`);
  }
</script>

<div class="page">
  <a href="/problems" class="back" on:click|preventDefault={() => push('/problems')}>
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
    {$t('problem.back')}
  </a>

  {#if loading}
    <div class="empty-state"><div class="spinner"></div><p>{$t('common.loading')}</p></div>
  {:else if problem}
    <header class="header">
      <div class="flex items-center gap-2 mb-4 flex-wrap">
        <span class={difficultyClass(problem.difficulty)}>
          {problem.difficulty === 'easy' ? $t('problems.diff.easy') : problem.difficulty === 'medium' ? $t('problems.diff.medium') : $t('problems.diff.hard')}
        </span>
        {#if problem.category}<span class="badge">{problem.category}</span>{/if}
        <span class="text-xs text-3">{$t('problem.meta', { time: problem.time_limit, memory: problem.memory_limit, count: problem.solved_count })}</span>
      </div>
      <h1>{problem.title}</h1>
    </header>

    <div class="layout">
      <div class="statement">
        {@html renderMarkdown(problem.statement || 'Условие недоступно.')}
        {#if problem.input_format}<h3>{$t('problem.input')}</h3><p>{@html renderMarkdown(problem.input_format)}</p>{/if}
        {#if problem.output_format}<h3>{$t('problem.output')}</h3><p>{@html renderMarkdown(problem.output_format)}</p>{/if}
        {#if problem.notes}<h3>Эзоҳ</h3><p>{@html renderMarkdown(problem.notes)}</p>{/if}
      </div>

      <aside class="aside">
        <h3>{$t('problem.sampleTests')}</h3>
        {#if sampleTests.length === 0}
          <p class="text-3 text-sm">{$t('problem.noSamples')}</p>
        {:else}
          {#each sampleTests as test, i}
            <div class="test-case">
              <div class="test-case__header">{$t('problem.test')} {i + 1}</div>
              <div class="mb-2"><strong class="text-xs text-3">{$t('problem.input')}</strong><pre>{test.input_data}</pre></div>
              <div><strong class="text-xs text-3">{$t('problem.output')}</strong><pre>{test.expected_output}</pre></div>
            </div>
          {/each}
        {/if}
        <button class="btn btn--primary btn--block btn--lg mt-6" on:click={solve}>{$t('problem.solve')} →</button>
      </aside>
    </div>
  {/if}
</div>

<style>
  .back {
    display: inline-flex; align-items: center; gap: var(--sp-2);
    color: var(--text-3); font-size: var(--fs-sm); margin-bottom: var(--sp-4);
  }
  .back:hover { color: var(--text-1); }
  .header { margin-bottom: var(--sp-6); }
  .header h1 { font-size: var(--fs-3xl); letter-spacing: -0.02em; }
  .layout { display: grid; grid-template-columns: 1.6fr 1fr; gap: var(--sp-8); align-items: start; }
  .statement {
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-lg); padding: var(--sp-6);
    font-size: var(--fs-md); line-height: 1.7; color: var(--text-2);
  }
  .statement :global(h1), .statement :global(h2), .statement :global(h3) {
    color: var(--text-1); margin-top: var(--sp-4); margin-bottom: var(--sp-2);
  }
  .statement :global(h2) { font-size: var(--fs-md); }
  .statement :global(h3) { font-size: var(--fs-base); }
  .statement :global(p) { margin-bottom: var(--sp-3); }
  .statement :global(code) { color: var(--brand); font-family: 'JetBrains Mono', monospace; font-size: 0.92em; }
  .statement :global(pre) {
    background: var(--bg); padding: var(--sp-3);
    border-radius: var(--r-md); margin: var(--sp-3) 0; overflow-x: auto;
  }
  .aside {
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-lg); padding: var(--sp-5); position: sticky;
    top: calc(var(--navbar-h) + var(--sp-4));
  }
  .aside h3 { font-size: var(--fs-sm); text-transform: uppercase; color: var(--text-3); letter-spacing: 0.05em; margin-bottom: var(--sp-4); }
  .test-case {
    background: var(--bg); border: 1px solid var(--line-1);
    border-radius: var(--r-md); padding: var(--sp-4); margin-bottom: var(--sp-3);
  }
  .test-case__header { display: flex; justify-content: space-between; font-size: var(--fs-xs); color: var(--text-3); margin-bottom: var(--sp-2); text-transform: uppercase; letter-spacing: 0.04em; }
  .test-case pre { font-family: 'JetBrains Mono', monospace; font-size: var(--fs-xs); color: var(--text-2); white-space: pre-wrap; margin: 0; }
  @media (max-width: 920px) {
    .layout { grid-template-columns: 1fr; }
    .aside { position: static; }
  }
</style>
