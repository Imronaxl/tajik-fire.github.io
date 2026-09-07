<script>
  import { push } from '../router.js';
  import { user, logout, ready } from '../auth.js';
  import { toasts } from '../toast.js';
  import { initials } from '../utils.js';
  import { t } from '../../core/i18n/index.js';
  import LanguageSwitcher from './LanguageSwitcher.svelte';

  let menuOpen = false;
  let dropdownOpen = false;

  const navLinks = [
    { href: '/', key: 'nav.home' },
    { href: '/problems', key: 'nav.problems' },
    { href: '/olympiads', key: 'nav.contests' },
    { href: '/learning', key: 'nav.learning' },
    { href: '/leaderboard', key: 'nav.leaderboard' },
    { href: '/messenger', key: 'nav.messenger', auth: true },
  ];

  function go(href) {
    menuOpen = false;
    dropdownOpen = false;
    push(href);
  }

  async function handleLogout() {
    await logout();
    toasts.success($t('toast.signedOut'));
    push('/');
  }

  $: isActive = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };
</script>

<nav class="navbar">
  <div class="navbar__inner">
    <a href="/" class="brand" on:click|preventDefault={() => go('/')}>
      <div class="brand__logo">T</div>
      <div class="brand__text">
        <strong>{$t('brand.name')}</strong>
        <small>{$t('brand.tagline')}</small>
      </div>
    </a>

    <div class="menu" class:menu--open={menuOpen}>
      {#each navLinks as link}
        {#if !link.auth || $user}
          <a
            href={link.href}
            class="menu__link"
            class:active={isActive(link.href)}
            on:click|preventDefault={() => go(link.href)}
          >{$t(link.key)}</a>
        {/if}
      {/each}
    </div>

    <div class="actions">
      <LanguageSwitcher />

      {#if $user}
        <button class="btn btn--secondary btn--sm" on:click={() => dropdownOpen = !dropdownOpen}>
          <div class="avatar avatar--sm avatar--gradient">{initials($user.username)}</div>
          <span class="hide-mobile">{$user.username}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        {#if dropdownOpen}
          <div class="dropdown" on:click|self={() => dropdownOpen = false}>
            <a href="/profile" class="dropdown__item" on:click|preventDefault={() => go('/profile')}>{$t('nav.profile')}</a>
            <a href="/tasks" class="dropdown__item" on:click|preventDefault={() => go('/tasks')}>{$t('nav.tasks')}</a>
            <a href="/submissions" class="dropdown__item" on:click|preventDefault={() => go('/submissions')}>{$t('nav.submissions')}</a>
            <div class="dropdown__divider"></div>
            <button class="dropdown__item dropdown__item--danger" on:click={handleLogout}>{$t('nav.signout')}</button>
          </div>
        {/if}
      {:else}
        <a href="/login" class="btn btn--ghost btn--sm" on:click|preventDefault={() => go('/login')}>{$t('nav.signin')}</a>
        <a href="/register" class="btn btn--primary btn--sm" on:click|preventDefault={() => go('/register')}>{$t('nav.signup')}</a>
      {/if}

      <button class="btn btn--ghost btn--icon btn--sm mobile-toggle" on:click={() => menuOpen = !menuOpen} aria-label="Menu">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          {#if menuOpen}
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          {:else}
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          {/if}
        </svg>
      </button>
    </div>
  </div>
</nav>

<style>
  .navbar {
    position: sticky;
    top: 0;
    z-index: 200;
    height: var(--navbar-h);
    background: rgba(8, 9, 13, 0.78);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--line-1);
    display: flex;
    align-items: center;
  }
  .navbar__inner {
    display: flex; align-items: center; justify-content: space-between;
    width: 100%; max-width: var(--layout-max); margin: 0 auto;
    padding: 0 var(--sp-6); gap: var(--sp-6);
  }
  .brand { display: flex; align-items: center; gap: var(--sp-3); cursor: pointer; }
  .brand__logo {
    width: 32px; height: 32px; border-radius: var(--r-md);
    background: linear-gradient(135deg, var(--brand) 0%, var(--purple) 100%);
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 700; color: #fff; font-size: var(--fs-md);
    box-shadow: 0 4px 12px var(--brand-glow); position: relative;
  }
  .brand__logo::after {
    content: ''; position: absolute; inset: 1px; border-radius: inherit;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  .brand__text { display: flex; flex-direction: column; line-height: 1.1; }
  .brand__text strong { font-weight: 700; }
  .brand__text small {
    font-size: 10px; color: var(--text-3); letter-spacing: 0.08em;
    text-transform: uppercase; font-weight: 500;
  }
  .menu {
    display: flex; align-items: center; gap: var(--sp-1);
    flex: 1; justify-content: center;
  }
  .menu__link {
    padding: 7px 12px; font-size: var(--fs-sm); color: var(--text-2);
    border-radius: var(--r-md); transition: all var(--ease);
  }
  .menu__link:hover { color: var(--text-1); background: var(--bg-surface); }
  .menu__link.active { color: var(--text-1); background: var(--bg-elevated); }
  .actions { display: flex; align-items: center; gap: var(--sp-3); }
  .mobile-toggle { display: none; }

  .dropdown {
    position: absolute; top: calc(var(--navbar-h) - 8px); right: var(--sp-6);
    min-width: 200px; background: var(--bg-elevated); border: 1px solid var(--line-2);
    border-radius: var(--r-md); box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
    padding: var(--sp-2); z-index: 300; animation: fade-in var(--ease);
  }
  .dropdown__item {
    display: flex; align-items: center; gap: var(--sp-3);
    padding: var(--sp-3); border-radius: var(--r-sm);
    color: var(--text-2); font-size: var(--fs-sm); transition: all var(--ease);
    width: 100%; text-align: left;
  }
  .dropdown__item:hover { background: var(--bg-surface); color: var(--text-1); }
  .dropdown__item--danger:hover { color: var(--bad); }
  .dropdown__divider { height: 1px; background: var(--line-1); margin: var(--sp-2) 0; }

  @media (max-width: 760px) {
    .menu {
      position: fixed; inset: var(--navbar-h) 0 0 0; background: var(--bg);
      flex-direction: column; align-items: stretch; padding: var(--sp-4);
      gap: var(--sp-2); transform: translateX(100%); transition: transform var(--ease); z-index: 200;
    }
    .menu--open { transform: translateX(0); }
    .menu__link { padding: var(--sp-4); font-size: var(--fs-md); }
    .mobile-toggle { display: inline-flex; }
    .brand__text small { display: none; }
  }
</style>
