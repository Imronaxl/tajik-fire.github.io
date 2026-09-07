import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  compilerOptions: {
    accessors: false,
  },
  onwarn(warning, defaultHandler) {
    const code = warning.code || '';
    if (code.startsWith('a11y')) return;
    defaultHandler(warning);
  },
};
