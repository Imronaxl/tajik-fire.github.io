<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { user } from '../../lib/auth.js';
  import { toasts } from '../../lib/toast.js';
  import { renderMarkdown, difficultyClass } from '../../lib/utils.js';
  import { t } from '../../core/i18n/index.js';

  export let params;

  let module = null;
  let loading = true;

  onMount(async () => {
    if (!$user) {
      toasts.warning($t('toast.loginRequired'));
      setTimeout(() => push(`/login?next=/learning/${params.slug}`), 800);
      return;
    }
    try {
      module = await api.get(`/learning/modules/${params.slug}`);
    } catch (err) {
      toasts.error($t('learning.notFound'));
    } finally {
      loading = false;
    }
  });
</script>

<div class="page">
  <a href="/learning" class="back" on:click|preventDefault={() => push('/learning')}>
    ← {$t('learning.backToModules')}
  </a>

  {#if loading}
    <div class="empty-state"><div class="spinner"></div><p>{$t('common.loading')}</p></div>
  {:else if module}
    <header class="header">
      <h1>{module.title}</h1>
      <p class="text-2 mt-2">{module.description}</p>
    </header>

    <div class="layout">
      <div class="theory">
        {@html renderMarkdown(module.theory_content || $t('learning.theory'))}
      </div>
      <aside class="problems">
        <h3>{$t('learning.problems')}</h3>
        {#if (module.problems || []).length === 0}
          <p class="text-3 text-sm">{$t('learning.noProblems')}</p>
        {:else}
          {#each module.problems as p}
            <a class="problem-row" href={`/problems/${p.id}`} on:click|preventDefault={() => push(`/problems/${p.id}`)}>
              <span class="problem-row__order">{String(p.order).padStart(2, '0')}</span>
              <span class="problem-row__title">{p.title}</span>
              <span class={difficultyClass(p.difficulty)}>
                {p.difficulty === 'easy' ? $t('problems.diff.easy') : p.difficulty === 'medium' ? $t('problems.diff.medium') : $t('problems.diff.hard')}
              </span>
            </a>
          {/each}
        {/if}
      </aside>
    </div>
  {/if}
</div>

<style>
  .back { display: inline-block; color: var(--text-3); font-size: var(--fs-sm); margin-bottom: var(--sp-4); }
  .back:hover { color: var(--text-1); }
  .header { margin-bottom: var(--sp-6); }
  .header h1 { font-size: var(--fs-3xl); letter-spacing: -0.02em; }
  .layout { display: grid; grid-template-columns: 1.4fr 1fr; gap: var(--sp-6); align-items: start; }
  .theory {
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-lg); padding: var(--sp-6);
    font-size: var(--fs-sm); line-height: 1.7; color: var(--text-2);
  }
  .theory :global(h1), .theory :global(h2), .theory :global(h3) { color: var(--text-1); margin-top: var(--sp-4); }
  .theory :global(h2) { font-size: var(--fs-md); }
  .theory :global(h3) { font-size: var(--fs-base); }
  .theory :global(p) { margin-bottom: var(--sp-3); }
  .theory :global(ul) { padding-left: var(--sp-5); list-style: disc; }
  .theory :global(li) { margin-bottom: var(--sp-1); }
  .problems {
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-lg); padding: var(--sp-5); position: sticky;
    top: calc(var(--navbar-h) + var(--sp-4));
  }
  .problems h3 { font-size: var(--fs-sm); text-transform: uppercase; color: var(--text-3); letter-spacing: 0.05em; margin-bottom: var(--sp-4); }
  .problem-row { display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-3); border-radius: var(--r-md); transition: background var(--ease); color: inherit; }
  .problem-row:hover { background: var(--bg-elevated); }
  .problem-row__order { font-family: 'JetBrains Mono', monospace; font-size: var(--fs-xs); color: var(--text-3); width: 24px; }
  .problem-row__title { flex: 1; font-size: var(--fs-sm); font-weight: 500; }
  @media (max-width: 920px) {
    .layout { grid-template-columns: 1fr; }
    .problems { position: static; }
  }
</style>
