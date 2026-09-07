import { writable } from 'svelte/store';
import api from './api.js';

export const user = writable(null);
export const ready = writable(false);

const TOKEN_KEY = 'tf_access_token';
const REFRESH_KEY = 'tf_refresh_token';

let initialized = false;

export async function initAuth() {
  if (initialized) return;
  initialized = true;
  if (!api.isAuthenticated()) {
    ready.set(true);
    return;
  }
  try {
    const me = await api.get('/auth/me');
    user.set(me);
  } catch (_) {
    api.clearTokens();
    user.set(null);
  }
  ready.set(true);
}

export async function login(credentials) {
  const data = await api.post('/auth/login', credentials);
  api.setTokens(data.access_token, data.refresh_token);
  user.set(data.user);
  return data.user;
}

export async function logout() {
  try { await api.post('/auth/logout'); } catch (_) { }
  api.clearTokens();
  user.set(null);
}

export async function register(payload) {
  return api.post('/auth/register', payload);
}

export async function confirmEmail(email, code) {
  return api.post('/auth/confirm-email', { email, code });
}

export async function resendCode(email) {
  return api.post('/auth/resend-code', { email });
}

export async function requestPasswordReset(email) {
  return api.post('/auth/reset-password-request', { email });
}

export async function resetPassword(email, code, newPassword) {
  return api.post('/auth/reset-password-confirm', { email, code, new_password: newPassword });
}

export async function changePassword(oldPwd, newPwd) {
  return api.post('/auth/change-password', { old_password: oldPwd, new_password: newPwd });
}

export async function updateProfile(payload) {
  const me = await api.put('/auth/profile', payload);
  user.set(me);
  return me;
}

window.addEventListener('storage', (e) => {
  if (e.key === TOKEN_KEY) {
    if (!e.newValue) user.set(null);
    else initAuth();
  }
});
