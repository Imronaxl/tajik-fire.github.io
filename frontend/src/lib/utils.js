export function initials(name) {
  if (!name) return '?';
  return name.split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase() || '').join('');
}

export function escapeHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function formatDate(value, opts = {}) {
  if (!value) return '—';
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return '—';
  if (opts.relative) return relativeTime(d);
  const lang = (typeof document !== 'undefined' && document.documentElement.lang) || 'tg';
  return d.toLocaleString(lang === 'tg' ? 'ru-RU' : lang, {
    year: 'numeric', month: 'short', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  });
}

export function relativeTime(d) {
  const diff = (Date.now() - d.getTime()) / 1000;
  const lang = (typeof document !== 'undefined' && document.documentElement.lang) || 'tg';
  if (lang === 'tg') {
    if (diff < 5) return 'ҳозир';
    if (diff < 60) return `${Math.floor(diff)} сония пеш`;
    if (diff < 3600) return `${Math.floor(diff / 60)} дақиқа пеш`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} соат пеш`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} рӯз пеш`;
    return d.toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' });
  }
  if (diff < 5) return 'только что';
  if (diff < 60) return `${Math.floor(diff)} сек назад`;
  if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`;
  if (diff < 604800) return `${Math.floor(diff / 86400)} дн назад`;
  return d.toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' });
}

export function difficultyClass(d) {
  return `diff diff--${(d || 'easy').toLowerCase()}`;
}

export function verdictClass(v) {
  if (!v) return 'badge';
  const x = v.toLowerCase();
  if (x === 'accepted') return 'badge badge--ok';
  if (x === 'wrong_answer') return 'badge badge--bad';
  if (x === 'pending' || x === 'judging') return 'badge badge--brand';
  if (x === 'time_limit_exceeded' || x === 'memory_limit_exceeded') return 'badge badge--warn';
  return 'badge';
}

export function verdictLabel(v, t) {
  if (!v) return '—';
  const map = {
    accepted: 'verdict.accepted',
    wrong_answer: 'verdict.wrongAnswer',
    time_limit_exceeded: 'verdict.tle',
    memory_limit_exceeded: 'verdict.mle',
    runtime_error: 'verdict.runtimeError',
    compilation_error: 'verdict.compileError',
    pending: 'verdict.pending',
    judging: 'verdict.judging',
  };
  const key = map[v] || map[v.toLowerCase()];
  if (key && t) return t(key);
  return v;
}

export function languageLabel(l) {
  return ({ python3: 'Python 3', cpp17: 'C++ 17', java11: 'Java 11' })[l] || l;
}

export function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => `<pre class="code-block">${escapeHtml(code)}</pre>`)
    .replace(/`([^`]+)`/g, (_, c) => `<code class="code-inline">${escapeHtml(c)}</code>`)
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<)(.+)$/gm, '<p>$1</p>')
    .replace(/<p><h/g, '<h')
    .replace(/<\/h\d><\/p>/g, '</h$1>');
}

export function debounce(fn, wait = 250) {
  let t;
  return function debounced(...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), wait);
  };
}

export function copy(text) {
  if (navigator.clipboard) return navigator.clipboard.writeText(text);
  return Promise.reject(new Error('clipboard api unavailable'));
}

export async function poll(fn, { interval = 800, timeout = 8000, shouldStop } = {}) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const tick = async () => {
      try {
        const value = await fn();
        if (shouldStop ? shouldStop(value) : true) return resolve(value);
      } catch (err) { return reject(err); }
      if (Date.now() - start >= timeout) return reject(new Error('poll timeout'));
      setTimeout(tick, interval);
    };
    tick();
  });
}
