<script>
  import { i18n, t } from '../i18n/index.js';
  import { SUPPORTED_LANGUAGES } from '../i18n/config.js';

  let open = false;

  function toggle() {
    open = !open;
  }

  function choose(code) {
    i18n.setLanguage(code);
    open = false;
  }

  function handleClickOutside(e) {
    if (!e.target.closest('.lang-switcher')) open = false;
  }

  $: current = $i18n.current || 'tg';
  $: currentLang = SUPPORTED_LANGUAGES.find((l) => l.code === current);
</script>

<svelte:window on:click={handleClickOutside} />

<div class="lang-switcher">
  <button class="lang-btn" on:click={toggle} aria-label={$t('language.toggle')}>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="2" y1="12" x2="22" y2="12"></line>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
    </svg>
    <span class="hide-mobile">{currentLang?.nativeName || current.toUpperCase()}</span>
  </button>
  {#if open}
    <div class="lang-menu">
      {#each SUPPORTED_LANGUAGES as lang}
        <button class="lang-item" class:active={lang.code === current} on:click={() => choose(lang.code)}>
          {lang.nativeName}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .lang-switcher { position: relative; }
  .lang-btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 10px; border-radius: 6px;
    background: var(--bg-elevated); border: 1px solid var(--line-2);
    color: var(--text-2); font-size: 13px; cursor: pointer;
    transition: all 200ms;
  }
  .lang-btn:hover { color: var(--text-1); border-color: var(--line-3); }
  .lang-menu {
    position: absolute; top: calc(100% + 4px); right: 0;
    min-width: 140px; background: var(--bg-elevated);
    border: 1px solid var(--line-2); border-radius: 8px;
    padding: 4px; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
    z-index: 300; animation: fade-in 200ms ease;
  }
  .lang-item {
    width: 100%; text-align: left; padding: 8px 10px;
    border-radius: 6px; color: var(--text-2);
    font-size: 13px; cursor: pointer; transition: all 200ms;
  }
  .lang-item:hover { background: var(--bg-surface); color: var(--text-1); }
  .lang-item.active { color: var(--brand); background: var(--brand-soft); }
  @media (max-width: 720px) {
    .hide-mobile { display: none; }
  }
</style>
