import api from '../api.js';
import { $, escapeHtml, relativeTime, verdictClass, verdictLabel, languageLabel } from '../utils/helpers.js';

const CODE_SAMPLES = {
  python: `<span class="kw">def</span> <span class="fn">main</span>():
    a, b = <span class="fn">map</span>(<span class="fn">int</span>, <span class="fn">input</span>().<span class="fn">split</span>())
    <span class="fn">print</span>(a + b)

<span class="fn">main</span>()`,
  cpp: `<span class="kw">#include</span> <span class="str">&lt;iostream&gt;</span>
<span class="kw">using namespace</span> std;

<span class="kw">int</span> <span class="fn">main</span>() {
    <span class="kw">int</span> a, b;
    cin &gt;&gt; a &gt;&gt; b;
    cout &lt;&lt; a + b &lt;&lt; <span class="str">'\\n'</span>;
    <span class="kw">return</span> <span class="num">0</span>;
}`,
  java: `<span class="kw">import</span> java.util.Scanner;

<span class="kw">public class</span> Main {
    <span class="kw">public static void</span> <span class="fn">main</span>(String[] args) {
        Scanner sc = <span class="kw">new</span> Scanner(System.in);
        <span class="kw">int</span> a = sc.nextInt(), b = sc.nextInt();
        System.out.println(a + b);
    }
}`,
};

document.addEventListener('DOMContentLoaded', async () => {
  bindCodeTabs();
  loadStats();
  loadFeed();
});

function bindCodeTabs() {
  const tabs = document.querySelectorAll('.code-tab');
  const preview = document.getElementById('code-preview');
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      const lang = tab.dataset.lang;
      preview.innerHTML = CODE_SAMPLES[lang] || CODE_SAMPLES.python;
    });
  });
}

async function loadStats() {
  try {
    const stats = await api.get('/stats/dashboard');
    setText('stat-problems', stats.total_problems);
    setText('stat-users', stats.total_users);
    setText('stat-submissions', stats.total_submissions);
    setText('stat-accepted', `${stats.accepted_rate}%`);
  } catch (_) { }
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

async function loadFeed() {
  const container = document.getElementById('home-feed');
  try {
    const items = await api.get('/stats/feed', { limit: 8 });
    if (!items || items.length === 0) {
      container.innerHTML = `
        <div class="feed-empty">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          No submissions yet. Be the first to climb the board!
        </div>`;
      return;
    }
    container.innerHTML = items.map((entry) => `
      <a class="feed-row" href="/problems/${entry.problem_id}">
        <div class="feed-row__user">
          <div class="avatar avatar--sm avatar--gradient">${escapeHtml(entry.username[0]?.toUpperCase() || '?')}</div>
          <div>
            <strong>${escapeHtml(entry.username)}</strong>
            <div class="text-xs text-tertiary">${relativeTime(new Date(entry.created_at))}</div>
          </div>
        </div>
        <div class="feed-row__main">
          <strong>${escapeHtml(entry.problem_title)}</strong>
          <span>${languageLabel(entry.language)}</span>
        </div>
        <div class="feed-row__meta">
          <span class="${verdictClass(entry.verdict)}">${verdictLabel(entry.verdict)}</span>
          ${entry.execution_time ? `<span>${entry.execution_time}s</span>` : ''}
        </div>
      </a>
    `).join('');
  } catch (_) {
    container.innerHTML = `<div class="feed-empty">Could not load feed. Try again later.</div>`;
  }
}
