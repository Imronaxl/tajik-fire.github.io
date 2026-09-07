<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { user } from '../../lib/auth.js';
  import { escapeHtml, initials, relativeTime, verdictClass, verdictLabel, languageLabel } from '../../lib/utils.js';
  import { t } from '../../core/i18n/index.js';

  let stats = { total_users: 0, total_problems: 0, total_submissions: 0, accepted_rate: 0 };
  let feed = [];

  const CODE_SAMPLES = {
    python: `def main():
    a, b = map(int, input().split())
    print(a + b)

main()`,
    cpp: `#include <bits/stdc++.h>
using namespace std;
int main() {
    int a, b; cin >> a >> b;
    cout << a + b << '\\n';
}`,
    java: `import java.util.Scanner;
public class Main {
    public static void main(String[] a) {
        Scanner s = new Scanner(System.in);
        System.out.println(s.nextInt() + s.nextInt());
    }
}`,
  };

  let activeLang = 'python';

  onMount(() => {
    loadStats();
    loadFeed();
  });

  async function loadStats() {
    try {
      const s = await api.get('/stats/dashboard');
      stats = s;
    } catch (_) { }
  }

  async function loadFeed() {
    try {
      feed = await api.get('/stats/feed', { limit: 8 });
    } catch (_) { }
  }
</script>

<section class="hero">
  <div class="container">
    <div class="hero__inner">
      <div>
        <span class="hero__tag">{$t('home.hero.tag')}</span>
        <h1>{$t('home.hero.title1')}<br />{$t('home.hero.title2')}<br /><span class="accent">{$t('home.hero.title3')}</span></h1>
        <p class="hero__sub">{$t('home.hero.subtitle')}</p>
        <div class="hero__actions">
          <button class="btn btn--primary btn--lg" on:click={() => push($user ? '/problems' : '/register')}>
            {$t('home.hero.cta.start')}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
          <button class="btn btn--secondary btn--lg" on:click={() => push('/problems')}>{$t('home.hero.cta.browse')}</button>
        </div>
        <div class="hero__meta">
          <div class="hero__meta-item"><strong>{stats.total_problems}</strong><small>{$t('home.hero.stats.problems')}</small></div>
          <div class="hero__meta-item"><strong>{stats.total_users}</strong><small>{$t('home.hero.stats.users')}</small></div>
          <div class="hero__meta-item"><strong>{stats.total_submissions}</strong><small>{$t('home.hero.stats.submissions')}</small></div>
          <div class="hero__meta-item"><strong>{stats.accepted_rate}%</strong><small>{$t('home.hero.stats.acceptance')}</small></div>
        </div>
      </div>

      <div class="hero__panel">
        <div class="code-tabs">
          {#each Object.keys(CODE_SAMPLES) as lang}
            <button class="code-tab" class:active={activeLang === lang} on:click={() => activeLang = lang}>
              {lang === 'python' ? 'solution.py' : lang === 'cpp' ? 'solution.cpp' : 'Main.java'}
            </button>
          {/each}
        </div>
        <pre class="code-panel">{CODE_SAMPLES[activeLang]}</pre>
        <div class="code-result">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Verdict: <strong>Accepted</strong> · 4 / 4 tests · 28&nbsp;мс · 8&nbsp;МБ
        </div>
      </div>
    </div>
  </div>
</section>

<section class="container" style="margin-bottom: var(--sp-12);">
  <div class="section-header">
    <div>
      <h2>{$t('home.features.title')}</h2>
      <p>{$t('home.features.subtitle')}</p>
    </div>
  </div>
  <div class="grid grid--3">
    <div class="feature-card">
      <div class="feature-card__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
      </div>
      <h3>{$t('home.features.judger.title')}</h3>
      <p>{$t('home.features.judger.desc')}</p>
    </div>
    <div class="feature-card feature-card--purple">
      <div class="feature-card__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
      </div>
      <h3>{$t('home.features.learning.title')}</h3>
      <p>{$t('home.features.learning.desc')}</p>
    </div>
    <div class="feature-card feature-card--teal">
      <div class="feature-card__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
      </div>
      <h3>{$t('home.features.social.title')}</h3>
      <p>{$t('home.features.social.desc')}</p>
    </div>
    <div class="feature-card feature-card--warn">
      <div class="feature-card__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>
      </div>
      <h3>{$t('home.features.rating.title')}</h3>
      <p>{$t('home.features.rating.desc')}</p>
    </div>
    <div class="feature-card">
      <div class="feature-card__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path></svg>
      </div>
      <h3>{$t('home.features.tasks.title')}</h3>
      <p>{$t('home.features.tasks.desc')}</p>
    </div>
    <div class="feature-card feature-card--purple">
      <div class="feature-card__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
      </div>
      <h3>{$t('home.features.i18n.title')}</h3>
      <p>{$t('home.features.i18n.desc')}</p>
    </div>
  </div>
</section>

<section class="container" style="margin-bottom: var(--sp-16);">
  <div class="section-header">
    <div>
      <h2>{$t('home.feed.title')}</h2>
      <p>{$t('home.feed.subtitle')}</p>
    </div>
    <button class="btn btn--ghost btn--sm" on:click={() => push('/submissions')}>{$t('home.feed.viewAll')} →</button>
  </div>
  <div class="feed-list">
    {#if feed.length === 0}
      <div class="empty-state">
        <div class="spinner"></div>
        <p>{$t('common.loading')}</p>
      </div>
    {:else}
      {#each feed as entry}
        <a class="feed-row" href={`/problems/${entry.problem_id}`}>
          <div class="feed-row__user">
            <div class="avatar avatar--sm avatar--gradient">{initials(entry.username)}</div>
            <div>
              <strong>{entry.username}</strong>
              <div class="text-xs text-3">{relativeTime(new Date(entry.created_at))}</div>
            </div>
          </div>
          <div class="feed-row__main">
            <strong>{entry.problem_title}</strong>
            <span>{languageLabel(entry.language)}</span>
          </div>
          <div class="feed-row__meta">
            <span class={verdictClass(entry.verdict)}>{verdictLabel(entry.verdict)}</span>
            {#if entry.execution_time}<span>{entry.execution_time}s</span>{/if}
          </div>
        </a>
      {/each}
    {/if}
  </div>
</section>

<style>
  .hero {
    position: relative; padding: var(--sp-12) 0 var(--sp-16); overflow: hidden;
  }
  .hero::before {
    content: ''; position: absolute; top: -120px; right: -160px;
    width: 460px; height: 460px;
    background: radial-gradient(circle, var(--brand-glow) 0%, transparent 70%);
    filter: blur(60px); z-index: -1;
  }
  .hero__inner {
    display: grid; grid-template-columns: 1.2fr 0.8fr; gap: var(--sp-12); align-items: center;
  }
  .hero__tagline {
    display: inline-flex; align-items: center; gap: var(--sp-2);
    padding: 4px 12px; background: var(--brand-soft);
    border: 1px solid rgba(91, 140, 255, 0.25); border-radius: var(--r-full);
    font-size: var(--fs-xs); color: var(--brand); font-weight: 500;
    letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: var(--sp-5);
  }
  .hero h1 {
    font-size: var(--fs-4xl); line-height: 1.05;
    letter-spacing: -0.03em; font-weight: 800; margin-bottom: var(--sp-4);
  }
  .hero h1 .accent {
    background: linear-gradient(135deg, var(--brand) 0%, var(--purple) 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  .hero__sub {
    font-size: var(--fs-md); color: var(--text-2); max-width: 56ch;
    margin-bottom: var(--sp-6); line-height: 1.6;
  }
  .hero__actions { display: flex; gap: var(--sp-3); flex-wrap: wrap; }
  .hero__meta { margin-top: var(--sp-8); display: flex; gap: var(--sp-6); flex-wrap: wrap; }
  .hero__meta-item { display: flex; flex-direction: column; }
  .hero__meta-item strong {
    font-size: var(--fs-2xl); font-weight: 700; font-feature-settings: 'tnum'; letter-spacing: -0.02em;
  }
  .hero__meta-item small {
    font-size: var(--fs-xs); color: var(--text-3); text-transform: uppercase;
    letter-spacing: 0.06em; font-weight: 500;
  }
  .hero__panel {
    background: var(--bg-surface); border: 1px solid var(--line-2);
    border-radius: var(--r-2xl); padding: var(--sp-6);
    box-shadow: 0 14px 32px rgba(0, 0, 0, 0.45); position: relative; overflow: hidden;
  }
  .hero__panel::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 1px; background: linear-gradient(90deg, transparent, var(--brand), transparent);
  }
  .code-tabs { display: flex; gap: var(--sp-2); margin-bottom: var(--sp-3); border-bottom: 1px solid var(--line-1); }
  .code-tab {
    padding: var(--sp-2) var(--sp-3); font-size: var(--fs-xs); color: var(--text-3);
    border-bottom: 2px solid transparent; margin-bottom: -1px;
    transition: all var(--ease); font-family: 'JetBrains Mono', monospace;
  }
  .code-tab.active { color: var(--brand); border-bottom-color: var(--brand); }
  .code-panel {
    background: var(--bg); border: 1px solid var(--line-1);
    border-radius: var(--r-md); padding: var(--sp-4);
    font-family: 'JetBrains Mono', monospace; font-size: var(--fs-sm);
    line-height: 1.7; overflow-x: auto; color: var(--text-2);
    white-space: pre;
  }
  .code-result {
    margin-top: var(--sp-3); padding: var(--sp-3);
    background: var(--ok-soft); border-radius: var(--r-md);
    font-family: 'JetBrains Mono', monospace; font-size: var(--fs-xs);
    color: var(--ok); display: flex; align-items: center; gap: var(--sp-2);
  }
  @media (max-width: 920px) {
    .hero__inner { grid-template-columns: 1fr; }
    .hero h1 { font-size: var(--fs-3xl); }
    .hero__panel { order: -1; }
  }

  .feature-card {
    padding: var(--sp-6); background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-xl); transition: all var(--ease);
    position: relative; overflow: hidden;
  }
  .feature-card:hover { border-color: var(--line-2); transform: translateY(-2px); }
  .feature-card__icon {
    width: 40px; height: 40px; border-radius: var(--r-md);
    background: var(--brand-soft); color: var(--brand);
    display: inline-flex; align-items: center; justify-content: center; margin-bottom: var(--sp-4);
  }
  .feature-card--purple .feature-card__icon { background: var(--purple-soft); color: var(--purple); }
  .feature-card--teal .feature-card__icon { background: var(--teal-soft); color: var(--teal); }
  .feature-card--warn .feature-card__icon { background: var(--warn-soft); color: var(--warn); }
  .feature-card h3 { font-size: var(--fs-md); margin-bottom: var(--sp-2); }
  .feature-card p { color: var(--text-2); font-size: var(--fs-sm); line-height: 1.55; }

  .feed-list { background: var(--bg-surface); border: 1px solid var(--line-1); border-radius: var(--r-xl); overflow: hidden; }
  .feed-empty { padding: var(--sp-12) var(--sp-6); text-align: center; color: var(--text-3); }
  .feed-row {
    display: grid; grid-template-columns: auto 1fr auto; gap: var(--sp-4);
    padding: var(--sp-4) var(--sp-5); border-bottom: 1px solid var(--line-1);
    align-items: center; transition: background var(--ease); color: inherit;
  }
  .feed-row:last-child { border-bottom: none; }
  .feed-row:hover { background: var(--bg-elevated); }
  .feed-row__user { display: flex; align-items: center; gap: var(--sp-2); min-width: 160px; }
  .feed-row__main { display: flex; flex-direction: column; min-width: 0; }
  .feed-row__main strong { font-weight: 500; font-size: var(--fs-sm); }
  .feed-row__main span { font-size: var(--fs-xs); color: var(--text-3); }
  .feed-row__meta { display: flex; align-items: center; gap: var(--sp-3); font-size: var(--fs-xs); color: var(--text-3); }
  @media (max-width: 720px) {
    .feed-row { grid-template-columns: 1fr; }
    .feed-row__user { min-width: 0; }
    .feed-row__meta { justify-content: space-between; }
  }
</style>
