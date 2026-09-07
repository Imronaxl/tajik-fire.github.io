export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}

const TOKEN_KEY = 'tf_access_token';
const REFRESH_KEY = 'tf_refresh_token';

class ApiClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.accessToken = localStorage.getItem(TOKEN_KEY);
    this.refreshToken = localStorage.getItem(REFRESH_KEY);
    this._refreshing = null;
  }

  getToken() { return this.accessToken; }

  setTokens(access, refresh) {
    this.accessToken = access;
    this.refreshToken = refresh;
    if (access) localStorage.setItem(TOKEN_KEY, access);
    else localStorage.removeItem(TOKEN_KEY);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
    else localStorage.removeItem(REFRESH_KEY);
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    window.dispatchEvent(new CustomEvent('auth:logout'));
  }

  isAuthenticated() { return !!this.accessToken; }

  async request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (this.accessToken) headers.set('Authorization', `Bearer ${this.accessToken}`);
    if (options.body && !headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
      options.body = JSON.stringify(options.body);
    }

    const response = await fetch(`${this.baseURL}${path}`, { ...options, headers });

    if (response.status === 401 && this.refreshToken && !options._retried) {
      const refreshed = await this._refresh();
      if (refreshed) return this.request(path, { ...options, _retried: true });
      this.clearTokens();
      throw new ApiError('session expired', 401);
    }

    if (!response.ok) {
      let payload = null;
      let message = `request failed (${response.status})`;
      try { payload = await response.json(); message = payload.detail || payload.message || message; } catch (_) { }
      throw new ApiError(message, response.status, payload);
    }

    if (response.status === 204) return null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) return response.json();
    return response.text();
  }

  async _refresh() {
    if (!this._refreshing) {
      this._refreshing = (async () => {
        try {
          const response = await fetch(`${this.baseURL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: this.refreshToken }),
          });
          if (!response.ok) return false;
          const data = await response.json();
          this.setTokens(data.access_token, data.refresh_token);
          return true;
        } catch (_) { return false; }
        finally { this._refreshing = null; }
      })();
    }
    return this._refreshing;
  }

  _withQuery(path, params) {
    if (!params) return path;
    const sp = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === null || v === '') continue;
      sp.append(k, v);
    }
    const qs = sp.toString();
    if (!qs) return path;
    return path.includes('?') ? `${path}&${qs}` : `${path}?${qs}`;
  }

  get(path, params) { return this.request(this._withQuery(path, params), { method: 'GET' }); }
  post(path, body, params) { return this.request(this._withQuery(path, params), { method: 'POST', body }); }
  put(path, body, params) { return this.request(this._withQuery(path, params), { method: 'PUT', body }); }
  patch(path, body, params) { return this.request(this._withQuery(path, params), { method: 'PATCH', body }); }
  delete(path, params) { return this.request(this._withQuery(path, params), { method: 'DELETE' }); }
}

export const api = new ApiClient();
export default api;
