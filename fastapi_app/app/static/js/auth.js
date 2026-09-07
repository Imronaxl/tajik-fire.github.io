import api from './api.js';

class AuthManager {
  constructor() {
    this.user = null;
    this._listeners = new Set();
  }

  async init() {
    if (!api.isAuthenticated()) {
      this._notify();
      return;
    }
    try {
      this.user = await api.get('/auth/me');
    } catch (_) {
      api.clearTokens();
      this.user = null;
    }
    this._notify();
  }

  async register(payload) {
    return api.post('/auth/register', payload);
  }

  async login(credentials) {
    const data = await api.post('/auth/login', credentials);
    api.setTokens(data.access_token, data.refresh_token);
    this.user = data.user;
    this._notify();
    return data.user;
  }

  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (_) { }
    api.clearTokens();
    this.user = null;
    this._notify();
  }

  async refresh() {
    const data = await api.post('/auth/refresh', { refresh_token: api.refreshToken });
    api.setTokens(data.access_token, data.refresh_token);
    this.user = data.user;
    this._notify();
    return data.user;
  }

  async confirmEmail(email, code) {
    return api.post('/auth/confirm-email', { email, code });
  }

  async resendCode(email) {
    return api.post('/auth/resend-code', { email });
  }

  async requestPasswordReset(email) {
    return api.post('/auth/reset-password-request', { email });
  }

  async resetPassword(email, code, newPassword) {
    return api.post('/auth/reset-password-confirm', { email, code, new_password: newPassword });
  }

  async changePassword(oldPassword, newPassword) {
    return api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword });
  }

  async updateProfile(payload) {
    const user = await api.put('/auth/profile', payload);
    this.user = user;
    this._notify();
    return user;
  }

  getUser() { return this.user; }
  isAuthenticated() { return !!this.user; }

  onChange(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  _notify() {
    this._listeners.forEach((fn) => fn(this.user));
  }
}

export const auth = new AuthManager();
export default auth;
