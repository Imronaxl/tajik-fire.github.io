const ICONS = {
  success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
  error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
  warning: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
  info: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
};

const DEFAULT_DURATION = 4200;

class ToastManager {
  constructor() {
    this.stack = document.getElementById('toast-stack');
    if (!this.stack) {
      this.stack = document.createElement('div');
      this.stack.className = 'toast-stack';
      this.stack.id = 'toast-stack';
      this.stack.setAttribute('aria-live', 'polite');
      document.body.appendChild(this.stack);
    }
  }

  show(message, type = 'info', options = {}) {
    const { title, duration = DEFAULT_DURATION } = options;
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.innerHTML = `
      <span class="toast__icon">${ICONS[type] || ICONS.info}</span>
      <div class="toast__content">
        ${title ? `<div class="toast__title">${escapeHtml(title)}</div>` : ''}
        <div class="toast__message">${escapeHtml(message)}</div>
      </div>
      <button class="toast__close" type="button" aria-label="Dismiss">×</button>
    `;
    this.stack.appendChild(toast);

    const close = () => {
      toast.classList.add('toast--leaving');
      setTimeout(() => toast.remove(), 200);
    };
    toast.querySelector('.toast__close').addEventListener('click', close);
    if (duration > 0) setTimeout(close, duration);

    return { close };
  }

  success(message, options) { return this.show(message, 'success', options); }
  error(message, options) { return this.show(message, 'error', { title: 'Error', ...options }); }
  warning(message, options) { return this.show(message, 'warning', options); }
  info(message, options) { return this.show(message, 'info', options); }

  fromError(err, options) {
    const message = err?.message || 'Something went wrong';
    return this.error(message, options);
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export const toast = new ToastManager();
export default toast;
