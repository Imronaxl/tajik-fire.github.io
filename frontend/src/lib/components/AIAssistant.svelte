<script>
  import { onMount } from 'svelte';
  import api from '../api.js';
  import { t } from '../../core/i18n/index.js';
  import { user } from '../auth.js';

  let open = false;
  let messages = [];
  let draft = '';
  let loading = false;

  function toggle() {
    open = !open;
  }

  async function send() {
    const text = draft.trim();
    if (!text || loading) return;
    draft = '';
    messages = [...messages, { role: 'user', content: text }];
    loading = true;
    try {
      const lang = (typeof document !== 'undefined' && document.documentElement.lang) || 'tg';
      const res = await api.post('/ai/chat', { message: text, language: lang });
      messages = [...messages, { role: 'assistant', content: res.reply }];
    } catch (err) {
      messages = [...messages, { role: 'assistant', content: err.message }];
    } finally {
      loading = false;
    }
  }
</script>

<button class="ai-fab" class:open on:click={toggle} aria-label={$t('ai.title')}>
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v2a3 3 0 0 0-3 3v2a3 3 0 0 0 3 3v2a3 3 0 0 0 3 3 3 3 0 0 0 3-3v-2a3 3 0 0 0 3-3v-2a3 3 0 0 0-3-3V5a3 3 0 0 0-3-3z"></path>
    <circle cx="9" cy="9" r="1"></circle>
    <circle cx="15" cy="9" r="1"></circle>
    <path d="M9 14c.83.67 1.83 1 3 1s2.17-.33 3-1"></path>
  </svg>
</button>

{#if open}
  <div class="ai-panel">
    <header class="ai-panel__header">
      <div class="flex items-center gap-2">
        <div class="ai-dot"></div>
        <strong>{$t('ai.panel.title')}</strong>
        <span class="badge badge--warn">{$t('ai.placeholder')}</span>
      </div>
      <button class="ai-panel__close" on:click={toggle} aria-label={$t('ai.panel.close')}>×</button>
    </header>
    <div class="ai-panel__body">
      {#if messages.length === 0}
        <div class="ai-empty">
          <p>{$t('ai.panel.empty')}</p>
          <p class="text-3 text-xs mt-2">{$t('ai.comingSoon')}</p>
        </div>
      {:else}
        {#each messages as msg, i}
          <div class="ai-msg ai-msg--{msg.role}">{msg.content}</div>
        {/each}
      {/if}
    </div>
    <form class="ai-panel__input" on:submit|preventDefault={send}>
      <input class="input" bind:value={draft} placeholder={$t('ai.panel.input')} disabled={loading}>
      <button class="btn btn--primary btn--icon" type="submit" disabled={loading || !draft.trim()}>
        {#if loading}
          <div class="spinner" style="width:14px;height:14px;border-width:2px;"></div>
        {:else}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        {/if}
      </button>
    </form>
  </div>
{/if}

<style>
  .ai-fab {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 999;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--brand) 0%, var(--purple) 100%);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 24px var(--brand-glow);
    transition: all 200ms;
  }
  .ai-fab:hover { transform: translateY(-2px) scale(1.05); }
  .ai-fab.open { transform: rotate(45deg); }

  .ai-panel {
    position: fixed;
    bottom: 88px;
    right: 24px;
    z-index: 999;
    width: 380px;
    max-width: calc(100vw - 48px);
    max-height: 560px;
    background: var(--bg-surface);
    border: 1px solid var(--line-2);
    border-radius: var(--r-xl);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: slide-up 250ms ease;
  }
  .ai-panel__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--sp-4) var(--sp-5);
    border-bottom: 1px solid var(--line-1);
  }
  .ai-panel__close {
    width: 28px;
    height: 28px;
    border-radius: var(--r-sm);
    color: var(--text-3);
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .ai-panel__close:hover { background: var(--bg-elevated); color: var(--text-1); }
  .ai-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--warn);
    box-shadow: 0 0 0 4px var(--warn-soft);
    animation: pulse 1.4s infinite;
  }
  .ai-panel__body {
    flex: 1;
    overflow-y: auto;
    padding: var(--sp-4);
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
    max-height: 380px;
  }
  .ai-empty {
    text-align: center;
    padding: var(--sp-8) var(--sp-4);
    color: var(--text-3);
    font-size: var(--fs-sm);
  }
  .ai-msg {
    padding: var(--sp-3) var(--sp-4);
    border-radius: var(--r-lg);
    font-size: var(--fs-sm);
    line-height: 1.5;
    max-width: 90%;
    word-wrap: break-word;
  }
  .ai-msg--user {
    background: var(--brand);
    color: #fff;
    align-self: flex-end;
    border-bottom-right-radius: var(--r-sm);
  }
  .ai-msg--assistant {
    background: var(--bg-elevated);
    color: var(--text-1);
    align-self: flex-start;
    border-bottom-left-radius: var(--r-sm);
  }
  .ai-panel__input {
    display: flex;
    gap: var(--sp-2);
    padding: var(--sp-3);
    border-top: 1px solid var(--line-1);
    background: var(--bg-surface);
  }
  .ai-panel__input .input { background: var(--bg); padding: 8px 10px; }
  @media (max-width: 720px) {
    .ai-panel { width: calc(100vw - 48px); right: 24px; bottom: 88px; }
    .ai-fab { bottom: 16px; right: 16px; }
  }
</style>
