<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import { login, register, confirmEmail, resendCode, requestPasswordReset, resetPassword } from '../../lib/auth.js';
  import { toasts } from '../../lib/toast.js';
  import { t } from '../../core/i18n/index.js';

  let tab = 'login';
  let pendingEmail = '';
  let lastRegistrationEmail = '';

  onMount(() => {
    const mode = new URLSearchParams(location.search).get('mode');
    if (mode && ['login', 'register', 'reset'].includes(mode)) tab = mode;
  });

  let form = {
    login: { login: '', password: '' },
    register: { first_name: '', last_name: '', username: '', email: '', password: '' },
    reset: { email: '' },
    resetConfirm: { code: '', new_password: '' },
    verify: { code: '' },
  };
  let loading = false;

  async function submitLogin() {
    loading = true;
    try {
      const u = await login(form.login);
      toasts.success($t('auth.toast.welcome', { name: u.username }));
      const next = new URLSearchParams(location.search).get('next') || '/problems';
      push(next);
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  }

  async function submitRegister() {
    loading = true;
    try {
      const result = await register(form.register);
      lastRegistrationEmail = form.register.email;
      if (result?.code) toasts.info($t('auth.toast.devCode', { code: result.code }), { duration: 8000 });
      else toasts.success($t('auth.toast.registered'));
      tab = 'verify';
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  }

  async function submitResetRequest() {
    loading = true;
    try {
      pendingEmail = form.reset.email;
      const result = await requestPasswordReset(form.reset.email);
      if (result?.code) toasts.info($t('auth.toast.devCode', { code: result.code }), { duration: 8000 });
      else toasts.success($t('auth.toast.codeSent'));
      tab = 'resetConfirm';
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  }

  async function submitResetConfirm() {
    loading = true;
    try {
      await resetPassword(pendingEmail, form.resetConfirm.code, form.resetConfirm.new_password);
      toasts.success($t('auth.toast.reset'));
      setTimeout(() => (tab = 'login'), 600);
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  }

  async function submitVerify() {
    loading = true;
    try {
      await confirmEmail(lastRegistrationEmail, form.verify.code);
      toasts.success($t('auth.toast.verified'));
      setTimeout(() => push('/login'), 800);
    } catch (err) { toasts.error(err.message); }
    finally { loading = false; }
  }

  async function doResend() {
    if (!lastRegistrationEmail) return toasts.warning($t('common.tryAgain'));
    const r = await resendCode(lastRegistrationEmail);
    if (r?.code) toasts.info($t('auth.toast.devCode', { code: r.code }), { duration: 8000 });
    else toasts.success($t('auth.toast.codeResent'));
  }

  const tabs = [
    { id: 'login', label: $t('auth.tab.login') },
    { id: 'register', label: $t('auth.tab.register') },
    { id: 'reset', label: $t('auth.tab.reset') },
  ];
</script>

<section class="auth">
  <div class="auth__card">
    <aside class="auth__aside">
      <div class="brand__logo" style="width:36px;height:36px;font-size:18px">T</div>
      <h2>{$t('auth.welcome.title')}</h2>
      <p>{$t('auth.welcome.subtitle')}</p>
      <div class="auth__demo">
        <span class="badge badge--brand">{$t('auth.demo.label')}</span>
        <code>{$t('auth.demo.hint')}</code>
      </div>
    </aside>

    <div class="auth__form-wrap">
      {#if tab !== 'verify' && tab !== 'resetConfirm'}
        <div class="auth__tabs">
          {#each tabs as tb}
            <button class="auth-tab" class:active={tab === tb.id} on:click={() => (tab = tb.id)}>{tb.label}</button>
          {/each}
        </div>
      {/if}

      {#if tab === 'login'}
        <form class="auth-form" on:submit|preventDefault={submitLogin}>
          <div class="field">
            <label class="field-label" for="login-username">{$t('auth.field.login')}</label>
            <input class="input" id="login-username" bind:value={form.login.login} type="text" autocomplete="username" required>
          </div>
          <div class="field">
            <label class="field-label" for="login-password">{$t('auth.field.password')}</label>
            <input class="input" id="login-password" bind:value={form.login.password} type="password" autocomplete="current-password" required>
          </div>
          <button class="btn btn--primary btn--block btn--lg" type="submit" disabled={loading}>
            {loading ? $t('auth.btn.logging') : $t('auth.btn.login')}
          </button>
          <a href="#" class="auth-link" on:click|preventDefault={() => (tab = 'reset')}>{$t('auth.link.forgot')}</a>
        </form>
      {:else if tab === 'register'}
        <form class="auth-form" on:submit|preventDefault={submitRegister}>
          <div class="field-row">
            <div class="field">
              <label class="field-label" for="reg-first">{$t('auth.field.firstName')}</label>
              <input class="input" id="reg-first" bind:value={form.register.first_name} type="text">
            </div>
            <div class="field">
              <label class="field-label" for="reg-last">{$t('auth.field.lastName')}</label>
              <input class="input" id="reg-last" bind:value={form.register.last_name} type="text">
            </div>
          </div>
          <div class="field">
            <label class="field-label" for="reg-username">{$t('auth.field.username')}</label>
            <input class="input" id="reg-username" bind:value={form.register.username} type="text" autocomplete="username" required>
          </div>
          <div class="field">
            <label class="field-label" for="reg-email">{$t('auth.field.email')}</label>
            <input class="input" id="reg-email" bind:value={form.register.email} type="email" autocomplete="email" required>
          </div>
          <div class="field">
            <label class="field-label" for="reg-password">{$t('auth.field.password')}</label>
            <input class="input" id="reg-password" bind:value={form.register.password} type="password" autocomplete="new-password" required>
            <p class="field-hint">{$t('auth.hint.password')}</p>
          </div>
          <button class="btn btn--primary btn--block btn--lg" type="submit" disabled={loading}>
            {loading ? $t('auth.btn.registering') : $t('auth.btn.register')}
          </button>
        </form>
      {:else if tab === 'reset'}
        <form class="auth-form" on:submit|preventDefault={submitResetRequest}>
          <div class="field">
            <label class="field-label" for="reset-email">{$t('auth.field.email')}</label>
            <input class="input" id="reset-email" bind:value={form.reset.email} type="email" autocomplete="email" required>
          </div>
          <button class="btn btn--primary btn--block btn--lg" type="submit" disabled={loading}>
            {loading ? $t('auth.btn.sending') : $t('auth.btn.sendCode')}
          </button>
        </form>
      {:else if tab === 'resetConfirm'}
        <form class="auth-form" on:submit|preventDefault={submitResetConfirm}>
          <div class="field">
            <label class="field-label" for="reset-code">{$t('auth.field.code')}</label>
            <input class="input" id="reset-code" bind:value={form.resetConfirm.code} type="text" required>
          </div>
          <div class="field">
            <label class="field-label" for="reset-new">{$t('auth.field.newPassword')}</label>
            <input class="input" id="reset-new" bind:value={form.resetConfirm.new_password} type="password" autocomplete="new-password" required>
          </div>
          <button class="btn btn--primary btn--block btn--lg" type="submit" disabled={loading}>
            {loading ? $t('auth.btn.resetting') : $t('auth.btn.reset')}
          </button>
        </form>
      {:else if tab === 'verify'}
        <form class="auth-form" on:submit|preventDefault={submitVerify}>
          <div class="field">
            <label class="field-label" for="verify-code">{$t('auth.field.code')}</label>
            <input class="input" id="verify-code" bind:value={form.verify.code} type="text" required>
            <p class="field-hint">{$t('auth.hint.code')}</p>
          </div>
          <button class="btn btn--primary btn--block btn--lg" type="submit" disabled={loading}>
            {loading ? $t('auth.btn.verifying') : $t('auth.btn.verify')}
          </button>
          <button type="button" class="btn btn--secondary btn--block" on:click={doResend} disabled={loading}>{$t('auth.btn.resend')}</button>
        </form>
      {/if}
    </div>
  </div>
</section>

<style>
  .auth {
    display: flex; justify-content: center; align-items: center;
    min-height: calc(100vh - var(--navbar-h) - 200px);
    padding: var(--sp-10) var(--sp-6);
  }
  .auth__card {
    display: grid; grid-template-columns: 0.8fr 1.2fr;
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-2xl); overflow: hidden;
    width: 100%; max-width: 880px; box-shadow: 0 14px 32px rgba(0, 0, 0, 0.45);
  }
  .auth__aside {
    padding: var(--sp-10) var(--sp-8);
    background: linear-gradient(180deg, var(--brand-soft) 0%, var(--bg-surface) 100%);
    border-right: 1px solid var(--line-1);
    display: flex; flex-direction: column; gap: var(--sp-4);
  }
  .auth__aside h2 { font-size: var(--fs-2xl); margin-top: var(--sp-4); letter-spacing: -0.02em; }
  .auth__aside p { color: var(--text-2); font-size: var(--fs-sm); line-height: 1.6; }
  .auth__demo {
    margin-top: auto; padding-top: var(--sp-6);
    border-top: 1px solid var(--line-1);
    display: flex; flex-direction: column; gap: var(--sp-2);
  }
  .auth__demo code {
    font-family: 'JetBrains Mono', monospace; font-size: var(--fs-sm);
    color: var(--brand); background: var(--bg);
    padding: 6px 10px; border-radius: var(--r-sm);
    display: inline-block; width: fit-content;
  }
  .auth__form-wrap { padding: var(--sp-8); }
  .auth__tabs {
    display: flex; gap: var(--sp-1); margin-bottom: var(--sp-6);
    border-bottom: 1px solid var(--line-1);
  }
  .auth-tab {
    padding: var(--sp-3) var(--sp-4); font-size: var(--fs-sm); font-weight: 500;
    color: var(--text-3); border-bottom: 2px solid transparent; margin-bottom: -1px;
    transition: all var(--ease);
  }
  .auth-tab:hover { color: var(--text-2); }
  .auth-tab.active { color: var(--text-1); border-bottom-color: var(--brand); }
  .auth-form { display: flex; flex-direction: column; gap: var(--sp-3); animation: fade-in var(--ease); }
  .auth-link {
    text-align: center; font-size: var(--fs-xs);
    color: var(--text-3); margin-top: var(--sp-2);
  }
  .auth-link:hover { color: var(--brand); }
  @media (max-width: 720px) {
    .auth__card { grid-template-columns: 1fr; max-width: 420px; }
    .auth__aside { display: none; }
    .auth__form-wrap { padding: var(--sp-6); }
  }
</style>
