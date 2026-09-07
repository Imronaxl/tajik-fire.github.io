<script>
  import { onMount, onDestroy } from 'svelte';
  import api from '../../lib/api.js';
  import { user } from '../../lib/auth.js';
  import { toasts } from '../../lib/toast.js';
  import { initials, formatDate } from '../../lib/utils.js';
  import { push } from '../../lib/router.js';
  import { t } from '../../core/i18n/index.js';

  let chats = [];
  let activeChat = null;
  let messages = [];
  let draft = '';
  let pollTimer = null;

  onMount(async () => {
    if (!$user) {
      toasts.warning($t('toast.loginRequired'));
      setTimeout(() => push(`/login?next=/messenger`), 800);
      return;
    }
    await loadChats();
    pollTimer = setInterval(refreshActive, 5000);
  });

  onDestroy(() => { if (pollTimer) clearInterval(pollTimer); });

  async function loadChats() {
    try {
      chats = await api.get('/messenger/chats');
      if (activeChat) {
        const chat = chats.find((c) => c.id === activeChat);
        if (chat) await loadMessages(chat.id);
      }
    } catch (_) { }
  }

  async function openChat(chatId) {
    activeChat = chatId;
    await loadMessages(chatId);
  }

  async function loadMessages(chatId) {
    try {
      messages = await api.get(`/messenger/chats/${chatId}/messages`, { limit: 100 });
      await tick();
      const wrap = document.querySelector('.messages');
      if (wrap) wrap.scrollTop = wrap.scrollHeight;
    } catch (_) { }
  }

  async function refreshActive() {
    if (!activeChat) return;
    await loadChats();
    await loadMessages(activeChat);
  }

  async function send() {
    const text = draft.trim();
    if (!text || !activeChat) {
      if (!text) toasts.warning($t('messenger.toast.empty'));
      return;
    }
    draft = '';
    try {
      await api.post('/messenger/messages', { chat_id: activeChat, content: text });
      await loadMessages(activeChat);
    } catch (err) { toasts.error(err.message); }
  }

  async function newChat() {
    const query = prompt($t('messenger.prompt.search'));
    if (!query) return;
    try {
      const users = await api.get('/users/search', { q: query });
      if (users.length === 0) return toasts.warning($t('messenger.noMatch'));
      const friend = users[0];
      await api.post('/messenger/chats', { is_group: false, member_ids: [friend.id] });
      toasts.success($t('messenger.toast.created', { name: friend.username }));
      await loadChats();
    } catch (err) { toasts.error(err.message); }
  }

  function peer(chat) {
    return (chat?.members || []).find((m) => m.id !== $user?.id) || chat?.members?.[0] || {};
  }

  import { tick } from 'svelte';
</script>

<div class="messenger">
  <aside class="sidebar">
    <header>
      <h2>{$t('messenger.title')}</h2>
      <button class="btn btn--secondary btn--icon btn--sm" on:click={newChat} title={$t('messenger.btn.new')} aria-label={$t('messenger.btn.new')}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
      </button>
    </header>
    <div class="chats-list">
      {#if chats.length === 0}
        <div class="empty-state" style="padding: var(--sp-8);">
          <h3>{$t('messenger.empty.chats')}</h3>
          <p class="text-xs">{$t('messenger.empty.chats.desc')}</p>
        </div>
      {:else}
        {#each chats as c}
          {@const p = peer(c)}
          <div class="chat-item" class:active={activeChat === c.id} on:click={() => openChat(c.id)} role="button" tabindex="0" aria-label={c.name || p.username}>
            <div class="avatar avatar--sm avatar--gradient">{initials(p.username || '?')}</div>
            <div class="chat-item__main">
              <div class="chat-item__name">{c.name || p.username || $t('messenger.group.default')}</div>
              <div class="chat-item__preview">{c.last_message?.content?.slice(0, 40) || $t('messenger.noMessages')}</div>
            </div>
            {#if c.unread_count > 0}<span class="unread">{c.unread_count}</span>{/if}
          </div>
        {/each}
      {/if}
    </div>
  </aside>

  <section class="window">
    {#if !activeChat}
      <div class="placeholder">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        <h3>{$t('messenger.placeholder')}</h3>
        <p>{$t('messenger.placeholder.desc')}</p>
      </div>
    {:else}
      {@const c = chats.find((x) => x.id === activeChat) || {}}
      {@const p = peer(c)}
      <header>
        <div class="avatar avatar--sm avatar--gradient">{initials(p.username || '?')}</div>
        <div>
          <div class="name">{c.name || p.username || $t('messenger.group.default')}</div>
          <div class="status text-xs text-3">{$t('messenger.direct')}</div>
        </div>
      </header>
      <div class="messages">
        {#each messages as m}
          <div class="bubble {$user && m.sender_id === $user.id ? 'mine' : 'theirs'}">
            {m.content}
            <div class="bubble__time">{formatDate(m.created_at)}</div>
          </div>
        {/each}
      </div>
      <form class="input-bar" on:submit|preventDefault={send}>
        <input class="input" bind:value={draft} placeholder={$t('messenger.input')} autocomplete="off">
        <button class="btn btn--primary btn--icon" type="submit" aria-label={$t('messenger.send')}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </form>
    {/if}
  </section>
</div>

<style>
  .messenger { display: grid; grid-template-columns: 320px 1fr; height: calc(100vh - var(--navbar-h)); background: var(--bg); flex: 1; }
  .sidebar { display: flex; flex-direction: column; border-right: 1px solid var(--line-1); background: var(--bg-surface); }
  .sidebar header { display: flex; align-items: center; justify-content: space-between; padding: var(--sp-4) var(--sp-5); border-bottom: 1px solid var(--line-1); }
  .sidebar header h2 { font-size: var(--fs-md); }
  .chats-list { flex: 1; overflow-y: auto; padding: var(--sp-2); }
  .chat-item { display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-3); border-radius: var(--r-md); cursor: pointer; transition: background var(--ease); margin-bottom: var(--sp-1); }
  .chat-item:hover { background: var(--bg-elevated); }
  .chat-item.active { background: var(--bg-elevated); }
  .chat-item__main { flex: 1; min-width: 0; }
  .chat-item__name { font-size: var(--fs-sm); font-weight: 500; margin-bottom: 2px; }
  .chat-item__preview { font-size: var(--fs-xs); color: var(--text-3); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .unread { background: var(--brand); color: #fff; font-size: var(--fs-xs); font-weight: 600; padding: 2px 6px; border-radius: var(--r-full); min-width: 18px; text-align: center; }

  .window { display: flex; flex-direction: column; background: var(--bg); overflow: hidden; }
  .placeholder { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: var(--sp-3); color: var(--text-3); }
  .window > header { display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-4) var(--sp-5); border-bottom: 1px solid var(--line-1); background: var(--bg-surface); }
  .name { font-weight: 600; font-size: var(--fs-sm); }
  .messages { flex: 1; overflow-y: auto; padding: var(--sp-5); display: flex; flex-direction: column; gap: var(--sp-3); }
  .bubble { max-width: 70%; padding: var(--sp-3) var(--sp-4); border-radius: var(--r-lg); font-size: var(--fs-sm); line-height: 1.5; word-wrap: break-word; }
  .bubble.mine { background: var(--brand); color: #fff; align-self: flex-end; border-bottom-right-radius: var(--r-sm); }
  .bubble.theirs { background: var(--bg-elevated); color: var(--text-1); align-self: flex-start; border-bottom-left-radius: var(--r-sm); }
  .bubble__time { font-size: 10px; color: var(--text-3); margin-top: 4px; }
  .bubble.mine .bubble__time { color: rgba(255, 255, 255, 0.7); }
  .input-bar { display: flex; gap: var(--sp-2); padding: var(--sp-4); border-top: 1px solid var(--line-1); background: var(--bg-surface); }
  .input-bar .input { background: var(--bg); }
  @media (max-width: 720px) {
    .messenger { grid-template-columns: 1fr; }
    .sidebar { display: none; }
    .bubble { max-width: 90%; }
  }
</style>
