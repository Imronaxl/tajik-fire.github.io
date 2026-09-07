import api from './api.js';
import auth from './auth.js';
import toast from './components/toast.js';
import { $$, initials } from './utils/helpers.js';

const NAV_SELECTORS = {
  navMenu: '#nav-menu',
  navToggle: '#nav-toggle',
  dropdown: '#user-dropdown',
  dropdownToggle: '#dropdown-toggle',
  logoutBtn: '#logout-btn',
  navAvatar: '#nav-avatar',
  navUsername: '#nav-username',
  loggedIn: '[data-auth="logged-in"]',
  loggedOut: '[data-auth="logged-out"]',
  search: '#global-search',
};

document.addEventListener('DOMContentLoaded', async () => {
  highlightActiveLink();
  bindNavToggle();
  bindUserDropdown();
  bindLogout();
  bindSearch();
  bindGlobalShortcuts();
  await auth.init();
  renderAuthState(auth.getUser());
  auth.onChange(renderAuthState);
});

function highlightActiveLink() {
  const path = window.location.pathname;
  $$('.navbar__link').forEach((link) => {
    const route = link.dataset.route;
    if (!route) return;
    const isActive = route === '/' ? path === '/' : path.startsWith(route);
    link.classList.toggle('active', isActive);
  });
}

function bindNavToggle() {
  const toggle = document.querySelector(NAV_SELECTORS.navToggle);
  const menu = document.querySelector(NAV_SELECTORS.navMenu);
  if (!toggle || !menu) return;
  toggle.addEventListener('click', () => menu.classList.toggle('navbar__menu--open'));
  menu.addEventListener('click', (e) => {
    if (e.target.matches('a')) menu.classList.remove('navbar__menu--open');
  });
}

function bindUserDropdown() {
  const dropdown = document.querySelector(NAV_SELECTORS.dropdown);
  const toggle = document.querySelector(NAV_SELECTORS.dropdownToggle);
  if (!dropdown || !toggle) return;
  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('dropdown--open');
  });
  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target)) dropdown.classList.remove('dropdown--open');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') dropdown.classList.remove('dropdown--open');
  });
}

function bindLogout() {
  const btn = document.querySelector(NAV_SELECTORS.logoutBtn);
  if (!btn) return;
  btn.addEventListener('click', async () => {
    await auth.logout();
    toast.success('Signed out. See you soon!');
    setTimeout(() => { window.location.href = '/'; }, 400);
  });
}

function bindSearch() {
  const input = document.querySelector(NAV_SELECTORS.search);
  if (!input) return;
  const params = new URLSearchParams(window.location.search);
  if (params.get('q')) input.value = params.get('q');

  input.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    const q = input.value.trim();
    if (q) window.location.href = `/problems?search=${encodeURIComponent(q)}`;
  });
}

function bindGlobalShortcuts() {
  document.addEventListener('keydown', (e) => {
    if (e.key !== '/' || e.target.matches('input,textarea')) return;
    const search = document.querySelector(NAV_SELECTORS.search);
    if (search) {
      e.preventDefault();
      search.focus();
    }
  });
}

function renderAuthState(user) {
  const loggedIn = $$(NAV_SELECTORS.loggedIn);
  const loggedOut = $$(NAV_SELECTORS.loggedOut);
  loggedIn.forEach((el) => { el.style.display = user ? '' : 'none'; });
  loggedOut.forEach((el) => { el.style.display = user ? 'none' : ''; });

  const avatar = document.querySelector(NAV_SELECTORS.navAvatar);
  const username = document.querySelector(NAV_SELECTORS.navUsername);
  if (avatar) {
    if (user) {
      avatar.textContent = initials(user.username || user.first_name || 'U');
      avatar.classList.add('avatar--gradient');
    } else {
      avatar.textContent = '?';
      avatar.classList.remove('avatar--gradient');
    }
  }
  if (username && user) username.textContent = user.username;

  $$('.navbar__link[data-auth="logged-in"]').forEach((link) => {
    link.style.display = user ? '' : 'none';
  });
}

window.addEventListener('storage', (e) => {
  if (e.key === 'access_token') {
    auth.init();
  }
});

window.addEventListener('unhandledrejection', (e) => {
  const message = e.reason?.message || 'Network request failed';
  if (e.reason?.status === 401) return;
  toast.error(message);
});

window.DevStudio = { api, auth, toast };
