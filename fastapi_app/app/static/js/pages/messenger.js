import api from '../api.js';
import auth from '../auth.js';
import toast from '../components/toast.js';
import { $, $$, escapeHtml, initials, formatDate } from '../utils/helpers.js';

const state = {
  chats: [],
  activeChat: null,
  pollTimer: null,
};

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.isAuthenticated()) {
    toast.warning('Sign in to use the messenger.');
    setTimeout(() => { window.location.href = '/login?next=/messenger'; }, 800);
    return;
  }
  bindNewChat();
  bindForm();
  await loadChats();
  startPolling();
});

function bindNewChat() {
  $('#new-chat-btn')?.addEventListener('click', async () => {
    const query = prompt('Search a user to start a chat with:');
    if (!query) return;
    try {
      const users = await api.get('/users/search', { q: query });
      if (users.length === 0) {
        toast.warning('No users matched.');
        return;
      }
      const friend = users[0];
      await api.post('/messenger/chats', {
        is_group: false,
        member_ids: [friend.id],
      });
      toast.success(`Chat with ${friend.username} created`);
      await loadChats();
    } catch (err) {
      toast.error(err.message);
    }
  });
}

function bindForm() {
  $('#chat-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const field = $('#chat-input-field');
    const text = field.value.trim();
    if (!text || !state.activeChat) return;
    field.value = '';
    try {
      await api.post('/messenger/messages', {
        chat_id: state.activeChat,
        content: text,
      });
      await loadMessages(state.activeChat);
    } catch (err) {
      toast.error(err.message);
    }
  });
}

async function loadChats() {
  const list = $('#chats-list');
  try {
    state.chats = await api.get('/messenger/chats');
    if (state.chats.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="padding: var(--space-8);">
          <h3>No chats yet</h3>
          <p class="text-xs">Start a new conversation.</p>
        </div>`;
      return;
    }
    list.innerHTML = state.chats.map((c) => {
      const peer = (c.members || []).find((m) => m.id !== auth.getUser()?.id) || c.members?.[0] || {};
      const lastMsg = c.last_message ? c.last_message.content : 'No messages yet';
      return `
        <div class="chat-list-item ${state.activeChat === c.id ? 'active' : ''}" data-id="${c.id}">
          <div class="avatar avatar--sm avatar--gradient">${escapeHtml(initials(peer.username || '?'))}</div>
          <div class="chat-list-item__main">
            <div class="chat-list-item__name">${escapeHtml(c.name || peer.username || 'Group chat')}</div>
            <div class="chat-list-item__preview">${escapeHtml(lastMsg.slice(0, 40))}</div>
          </div>
          ${c.unread_count > 0 ? `<span class="chat-list-item__unread">${c.unread_count}</span>` : ''}
        </div>`;
    }).join('');
    $$('.chat-list-item').forEach((item) => {
      item.addEventListener('click', () => openChat(parseInt(item.dataset.id, 10)));
    });
  } catch (err) {
    list.innerHTML = `<div class="empty-state"><p>${escapeHtml(err.message)}</p></div>`;
  }
}

async function openChat(chatId) {
  state.activeChat = chatId;
  $('#chat-empty').style.display = 'none';
  $('#chat-active').style.display = 'flex';
  const chat = state.chats.find((c) => c.id === chatId);
  const peer = chat?.members?.find((m) => m.id !== auth.getUser()?.id) || chat?.members?.[0];
  $('#chat-peer-name').textContent = chat?.name || peer?.username || 'Group chat';
  $('#chat-peer-avatar').textContent = initials(peer?.username || '?');
  $$('.chat-list-item').forEach((i) => i.classList.toggle('active', parseInt(i.dataset.id, 10) === chatId));
  await loadMessages(chatId);
}

async function loadMessages(chatId) {
  const wrap = $('#chat-messages');
  try {
    const messages = await api.get(`/messenger/chats/${chatId}/messages`, { limit: 100 });
    const me = auth.getUser();
    wrap.innerHTML = messages.map((m) => `
      <div class="message-bubble ${m.sender_id === me?.id ? 'message-bubble--mine' : 'message-bubble--theirs'}">
        ${escapeHtml(m.content)}
        <div class="message-bubble__time">${formatDate(m.created_at)}</div>
      </div>
    `).join('');
    wrap.scrollTop = wrap.scrollHeight;
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state"><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function startPolling() {
  state.pollTimer = setInterval(async () => {
    if (!state.activeChat) return;
    try {
      await loadChats();
      await loadMessages(state.activeChat);
    } catch (_) { }
  }, 5000);
}

window.addEventListener('beforeunload', () => {
  if (state.pollTimer) clearInterval(state.pollTimer);
});
