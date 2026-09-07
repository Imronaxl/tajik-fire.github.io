<script>
  import { push } from '../../lib/router.js';
  import { t } from '../../core/i18n/index.js';
</script>

<div class="page empty-state">
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
  <h1>{$t('404.title')}</h1>
  <p>{$t('404.desc')}</p>
  <button class="btn btn--primary btn--sm mt-4" on:click={() => push('/')}>{$t('404.home')}</button>
</div>
