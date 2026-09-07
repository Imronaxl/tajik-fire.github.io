export const SUPPORTED_LANGUAGES = [
  { code: 'tg', name: 'Тоҷикӣ', nativeName: 'Тоҷикӣ', dir: 'ltr', file: () => import('./locales/tg.json') },
  { code: 'ru', name: 'Русский', nativeName: 'Русский', dir: 'ltr', file: () => import('./locales/ru.json') },
  { code: 'en', name: 'English', nativeName: 'English', dir: 'ltr', file: () => import('./locales/en.json') },
];

export const DEFAULT_LANGUAGE = 'tg';
export const STORAGE_KEY = 'tf_lang';

export function getSupportedCodes() {
  return SUPPORTED_LANGUAGES.map((l) => l.code);
}
