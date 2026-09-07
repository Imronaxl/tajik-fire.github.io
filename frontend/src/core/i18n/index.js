import { writable, derived } from 'svelte/store';
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, STORAGE_KEY } from './config.js';

const caches = new Map();

function detectInitial() {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && SUPPORTED_LANGUAGES.some((l) => l.code === saved)) return saved;
  }
  if (typeof navigator !== 'undefined') {
    const browser = navigator.language?.slice(0, 2);
    if (browser && SUPPORTED_LANGUAGES.some((l) => l.code === browser)) return browser;
  }
  return DEFAULT_LANGUAGE;
}

function createI18nStore() {
  const current = writable(detectInitial());
  const translations = writable({});

  async function load(code) {
    if (caches.has(code)) return caches.get(code);
    const lang = SUPPORTED_LANGUAGES.find((l) => l.code === code);
    if (!lang) return {};
    const mod = await lang.file();
    caches.set(code, mod.default || mod);
    return caches.get(code);
  }

  async function setLanguage(code) {
    if (!SUPPORTED_LANGUAGES.some((l) => l.code === code)) return;
    const data = await load(code);
    current.set(code);
    translations.set(data);
    if (typeof localStorage !== 'undefined') localStorage.setItem(STORAGE_KEY, code);
    if (typeof document !== 'undefined') document.documentElement.lang = code;
  }

  const t = derived([current, translations], ([$current, $translations]) => {
    return (key, params = {}) => {
      const value = $translations[key] ?? key;
      if (typeof value !== 'string') return key;
      return value.replace(/\{(\w+)\}/g, (_, k) => (params[k] !== undefined ? params[k] : `{${k}}`));
    };
  });

  return {
    current,
    t,
    setLanguage,
    init: async () => {
      const code = detectInitial();
      await setLanguage(code);
    },
  };
}

export const i18n = createI18nStore();
export const t = i18n.t;
