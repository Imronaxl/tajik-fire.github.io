import { writable } from 'svelte/store';

let counter = 0;

function createToastStore() {
  const { subscribe, update } = writable([]);

  function push(message, type = 'info', opts = {}) {
    const id = ++counter;
    const toast = { id, message, type, title: opts.title, duration: opts.duration ?? 4200 };
    update((list) => [...list, toast]);
    if (toast.duration > 0) {
      setTimeout(() => dismiss(id), toast.duration);
    }
    return id;
  }

  function dismiss(id) {
    update((list) => list.filter((t) => t.id !== id));
  }

  return {
    subscribe,
    push,
    dismiss,
    success: (msg, opts) => push(msg, 'ok', opts),
    error: (msg, opts) => push(msg, 'bad', { title: 'Ошибка', ...opts }),
    warning: (msg, opts) => push(msg, 'warn', opts),
    info: (msg, opts) => push(msg, 'info', opts),
    fromError: (err, opts) => push(err?.message || 'Что-то пошло не так', 'bad', { title: 'Ошибка', ...opts }),
  };
}

export const toasts = createToastStore();
