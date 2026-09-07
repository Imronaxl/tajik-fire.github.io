<script>
  import { onMount, onDestroy } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { user } from '../../lib/auth.js';
  import { toasts } from '../../lib/toast.js';
  import { renderMarkdown, difficultyClass, verdictClass, verdictLabel, languageLabel, relativeTime, escapeHtml } from '../../lib/utils.js';

  export let params;

  let problem = null;
  let loading = true;
  let lang = 'python3';
  let code = '';
  let submitting = false;
  let results = [];
  let pollTimer = null;

  const STARTER = {
    python3: `def main():
    pass

main()`,
    cpp17: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    return 0;
}`,
    java11: `import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
    }
}`,
  };

  onMount(async () => {
    if (!$user) {
      toasts.warning('Войдите, чтобы отправлять решения.');
      setTimeout(() => push(`/login?next=/problems/${params.id}/solve`), 800);
      return;
    }
    try {
      const l = localStorage.getItem('preferred_lang') || 'en';
      problem = await api.get(`/problems/${params.id}`, { lang: l });
      const savedLang = localStorage.getItem('editor_lang') || 'python3';
      lang = savedLang;
      loadSaved();
    } catch (err) {
      toasts.error(err.message);
    } finally {
      loading = false;
    }
  });

  onDestroy(() => { if (pollTimer) clearInterval(pollTimer); });

  function loadSaved() {
    const saved = localStorage.getItem(`code:${params.id}:${lang}`);
    code = saved || STARTER[lang] || '';
  }

  function onLangChange(e) {
    lang = e.target.value;
    localStorage.setItem('editor_lang', lang);
    loadSaved();
  }

  function onCodeInput() {
    localStorage.setItem(`code:${params.id}:${lang}`, code);
  }

  function reset() {
    if (!confirm('Сбросить редактор к стартовому шаблону?')) return;
    code = STARTER[lang] || '';
    onCodeInput();
  }

  async function submit() {
    if (!code.trim()) return toasts.warning('Сначала напишите код.');
    submitting = true;
    try {
      const submission = await api.post('/problems/submissions', {
        problem_id: parseInt(params.id, 10),
        language: lang,
        code,
      });
      results = [{ ...submission, polling: true }, ...results];
      poll(submission.id);
    } catch (err) {
      toasts.error(err.message);
    } finally {
      submitting = false;
    }
  }

  function poll(submissionId) {
    let attempts = 0;
    pollTimer = setInterval(async () => {
      attempts++;
      try {
        const s = await api.get(`/problems/submissions/${submissionId}`);
        if (s.verdict && s.verdict !== 'pending' && s.verdict !== 'judging') {
          clearInterval(pollTimer);
          pollTimer = null;
          results = results.map((r) => (r.id === submissionId ? { ...s, polling: false } : r));
          if (s.verdict === 'accepted') {
            toasts.success(`Accepted! ${s.test_passed}/${s.test_total} тестов.`);
          } else {
            toasts.error(`${verdictLabel(s.verdict)} на тесте ${s.test_passed + 1}`);
          }
        }
      } catch (_) { }
      if (attempts > 30) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
    }, 800);
  }
</script>

<div class="editor-page">
  <div class="editor-layout">
    <aside class="aside">
      <a href="/problems" class="back" on:click|preventDefault={() => push('/problems')}>
        ← Архив
      </a>
      {#if loading}
        <div class="empty-state"><div class="spinner"></div></div>
      {:else if problem}
        <div class="header">
          <div class="flex items-center gap-2 mb-2 flex-wrap">
            <span class={difficultyClass(problem.difficulty)}>{problem.difficulty}</span>
            {#if problem.category}<span class="badge">{problem.category}</span>{/if}
          </div>
          <h1>{problem.title}</h1>
          <p class="text-xs text-3 mt-2">{problem.time_limit}s · {problem.memory_limit} MB · {problem.solved_count} решили</p>
        </div>
        <div class="statement">
          {@html renderMarkdown(problem.statement || 'Условие недоступно.')}
          {#if problem.input_format}<h3>Вход</h3><p>{@html renderMarkdown(problem.input_format)}</p>{/if}
          {#if problem.output_format}<h3>Выход</h3><p>{@html renderMarkdown(problem.output_format)}</p>{/if}
          {#if problem.notes}<h3>Примечание</h3><p>{@html renderMarkdown(problem.notes)}</p>{/if}
        </div>
      {/if}
    </aside>

    <section class="main">
      <header class="toolbar">
        <select class="select lang-select" value={lang} on:change={onLangChange}>
          <option value="python3">Python 3</option>
          <option value="cpp17">C++ 17</option>
          <option value="java11">Java 11</option>
        </select>
        <div class="flex items-center gap-2">
          <button class="btn btn--ghost btn--sm" on:click={reset}>Сбросить</button>
          <button class="btn btn--primary btn--sm" on:click={submit} disabled={submitting}>
            {#if submitting}
              <div class="spinner" style="width:14px;height:14px;border-width:2px;"></div>
              Отправка…
            {:else}
              Отправить
            {/if}
          </button>
        </div>
      </header>
      <textarea
        class="code"
        bind:value={code}
        on:input={onCodeInput}
        spellcheck="false"
        autocomplete="off"
        placeholder="// напишите решение здесь"
      ></textarea>
      <div class="results">
        {#if results.length === 0}
          <div class="empty-state">
            <p class="text-xs text-3">Отправьте код, чтобы увидеть вердикт.</p>
          </div>
        {:else}
          {#each results as r (r.id)}
            <div class="verdict-card verdict-card--{r.verdict === 'accepted' ? 'ok' : r.verdict === 'wrong_answer' ? 'bad' : 'warn'}">
              <div class="verdict-card__icon">
                {#if r.polling}
                  <div class="spinner" style="width:14px;height:14px;border-width:2px;"></div>
                {:else if r.verdict === 'accepted'}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                {:else}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                {/if}
              </div>
              <div class="verdict-card__main">
                <div class="verdict-card__title">Сабмит #{r.id} · {languageLabel(r.language)}</div>
                <div class="verdict-card__meta">
                  {#if r.polling}
                    Judging…
                  {:else}
                    <span class={verdictClass(r.verdict)}>{verdictLabel(r.verdict)}</span>
                    · {r.test_passed}/{r.test_total} тестов
                    {#if r.execution_time}· {r.execution_time}s{/if}
                    {#if r.memory_used}· {r.memory_used} MB{/if}
                    · {relativeTime(new Date(r.created_at))}
                  {/if}
                </div>
                {#if r.error_message && !r.polling}
                  <div class="verdict-card__error">{r.error_message}</div>
                {/if}
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </section>
  </div>
</div>

<style>
  .editor-page { flex: 1; padding: 0; max-width: none; }
  .editor-layout {
    display: grid; grid-template-columns: 1fr 1fr;
    height: calc(100vh - var(--navbar-h)); background: var(--bg);
  }
  .aside {
    border-right: 1px solid var(--line-1); background: var(--bg-surface);
    display: flex; flex-direction: column; overflow: hidden;
  }
  .back { display: inline-block; padding: var(--sp-4) var(--sp-5); color: var(--text-3); font-size: var(--fs-sm); }
  .back:hover { color: var(--text-1); }
  .header { padding: 0 var(--sp-6) var(--sp-3); }
  .header h1 { font-size: var(--fs-xl); letter-spacing: -0.015em; }
  .statement {
    flex: 1; overflow-y: auto; padding: var(--sp-5) var(--sp-6);
    font-size: var(--fs-sm); line-height: 1.7; color: var(--text-2);
  }
  .statement :global(h1), .statement :global(h2), .statement :global(h3) { color: var(--text-1); margin-top: var(--sp-4); margin-bottom: var(--sp-2); }
  .statement :global(h2) { font-size: var(--fs-md); }
  .statement :global(h3) { font-size: var(--fs-base); }
  .statement :global(p) { margin-bottom: var(--sp-3); }
  .statement :global(code) { color: var(--brand); }
  .statement :global(pre) { background: var(--bg); padding: var(--sp-3); border-radius: var(--r-md); margin: var(--sp-3) 0; overflow-x: auto; }
  .main { display: flex; flex-direction: column; background: var(--bg); overflow: hidden; }
  .toolbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: var(--sp-3) var(--sp-4); border-bottom: 1px solid var(--line-1);
    background: var(--bg-surface);
  }
  .lang-select { width: 140px; background: var(--bg); padding: 6px 10px; font-size: var(--fs-sm); }
  .code {
    flex: 1; resize: none; padding: var(--sp-5);
    background: var(--bg); color: var(--text-1);
    font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.65;
    tab-size: 4; outline: none; border: none;
  }
  .results {
    max-height: 240px; overflow-y: auto;
    border-top: 1px solid var(--line-1); background: var(--bg-surface);
  }
  .verdict-card {
    padding: var(--sp-4) var(--sp-5); border-bottom: 1px solid var(--line-1);
    display: flex; align-items: center; gap: var(--sp-3); animation: fade-in var(--ease);
  }
  .verdict-card:last-child { border-bottom: none; }
  .verdict-card__icon {
    width: 28px; height: 28px; border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  .verdict-card--ok .verdict-card__icon { background: var(--ok-soft); color: var(--ok); }
  .verdict-card--bad .verdict-card__icon { background: var(--bad-soft); color: var(--bad); }
  .verdict-card--warn .verdict-card__icon { background: var(--warn-soft); color: var(--warn); }
  .verdict-card__main { flex: 1; min-width: 0; }
  .verdict-card__title { font-size: var(--fs-sm); font-weight: 600; margin-bottom: 2px; }
  .verdict-card__meta { font-size: var(--fs-xs); color: var(--text-3); font-family: 'JetBrains Mono', monospace; }
  .verdict-card__error {
    font-size: var(--fs-xs); color: var(--bad); margin-top: 4px;
    font-family: 'JetBrains Mono', monospace; white-space: pre-wrap;
    max-height: 80px; overflow-y: auto;
  }
  @media (max-width: 920px) {
    .editor-layout { grid-template-columns: 1fr; height: auto; }
    .aside { max-height: 50vh; }
    .main { min-height: 60vh; }
  }
</style>
