export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

export function el(tagName, props = {}, children = []) {
  const node = document.createElement(tagName);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class' || k === 'className') node.className = v;
    else if (k === 'dataset') Object.assign(node.dataset, v);
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2).toLowerCase(), v);
    else if (k === 'html') node.innerHTML = v;
    else if (v !== null && v !== undefined) node.setAttribute(k, v);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}

export function debounce(fn, wait = 250) {
  let t;
  return function debounced(...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), wait);
  };
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
  return d.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  });
}

export function relativeTime(d) {
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 5) return 'just now';
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export function initials(name) {
  if (!name) return '?';
  return name.split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase() || '').join('');
}

export function difficultyClass(difficulty) {
  return `difficulty difficulty--${(difficulty || 'easy').toLowerCase()}`;
}

export function verdictClass(verdict) {
  if (!verdict) return 'badge';
  const v = verdict.toLowerCase();
  if (v === 'accepted') return 'badge badge--success';
  if (v === 'wrong_answer') return 'badge badge--danger';
  if (v === 'pending' || v === 'judging') return 'badge badge--accent';
  if (v === 'time_limit_exceeded' || v === 'memory_limit_exceeded') return 'badge badge--warning';
  return 'badge';
}

export function verdictLabel(verdict) {
  const map = {
    accepted: 'Accepted',
    wrong_answer: 'Wrong answer',
    time_limit_exceeded: 'Time limit',
    memory_limit_exceeded: 'Memory limit',
    runtime_error: 'Runtime error',
    compilation_error: 'Compilation error',
    pending: 'Pending',
    judging: 'Judging',
  };
  return map[verdict] || verdict || '—';
}

export function languageLabel(language) {
  return ({
    python3: 'Python 3',
    cpp17: 'C++ 17',
    java11: 'Java 11',
  })[language] || language;
}

export function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => `<pre class="code-block">${escapeHtml(code)}</pre>`)
    .replace(/`([^`]+)`/g, (_, code) => `<code class="code-inline">${escapeHtml(code)}</code>`)
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<)(.+)$/gm, '<p>$1</p>')
    .replace(/<p><h/g, '<h')
    .replace(/<\/h\d><\/p>/g, '</h$1>');
}

export function copy(text) {
  if (navigator.clipboard) return navigator.clipboard.writeText(text);
  return Promise.reject(new Error('clipboard api unavailable'));
}

export function poll(fn, { interval = 800, timeout = 8000, shouldStop } = {}) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const tick = async () => {
      try {
        const value = await fn();
        if (shouldStop ? shouldStop(value) : true) return resolve(value);
      } catch (err) {
        return reject(err);
      }
      if (Date.now() - start >= timeout) return reject(new Error('poll timeout'));
      setTimeout(tick, interval);
    };
    tick();
  });
}
