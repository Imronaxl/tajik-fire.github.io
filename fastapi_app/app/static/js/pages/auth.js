import auth from '../auth.js';
import toast from '../components/toast.js';

const TAB_TO_FORM = {
  login: 'login-form',
  register: 'register-form',
  reset: 'reset-request-form',
};

let pendingEmail = '';
let lastRegistrationEmail = '';

document.addEventListener('DOMContentLoaded', () => {
  bindTabs();
  bindForms();
  const initial = new URLSearchParams(location.search).get('mode');
  if (initial && TAB_TO_FORM[initial]) switchTab(initial);
});

function bindTabs() {
  document.querySelectorAll('.auth-tab').forEach((tab) => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });
  document.querySelectorAll('[data-tab]').forEach((el) => {
    if (el.classList.contains('auth-tab')) return;
    el.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab(el.dataset.tab);
    });
  });
}

function switchTab(name) {
  document.querySelectorAll('.auth-tab').forEach((t) => {
    t.classList.toggle('active', t.dataset.tab === name);
  });
  document.querySelectorAll('.auth-form').forEach((f) => {
    f.classList.toggle('active', f.id === TAB_TO_FORM[name]);
  });
  document.querySelector(`#${TAB_TO_FORM[name]}`)?.scrollIntoView({ block: 'nearest' });
}

function bindForms() {
  form('login-form', async (data) => {
    const user = await auth.login(data);
    toast.success(`Welcome back, ${user.username}!`);
    const next = new URLSearchParams(location.search).get('next') || '/problems';
    window.location.href = next;
  });

  form('register-form', async (data) => {
    const result = await auth.register(data);
    lastRegistrationEmail = data.email;
    if (result && result.code) {
      toast.info(`Dev mode: your verification code is ${result.code}`, { duration: 8000 });
    } else {
      toast.success('Account created. Check your email for a 6-digit code.');
    }
    showVerifyForm();
  });

  form('reset-request-form', async (data) => {
    pendingEmail = data.email;
    const result = await auth.requestPasswordReset(data.email);
    if (result && result.code) {
      toast.info(`Dev mode: your reset code is ${result.code}`, { duration: 8000 });
    } else {
      toast.success('If the email exists, a reset code has been sent.');
    }
    switchTab('reset');
    document.querySelector('#reset-request-form').classList.remove('active');
    document.querySelector('#reset-confirm-form').classList.add('active');
  });

  form('reset-confirm-form', async (data) => {
    await auth.resetPassword(pendingEmail, data.code, data.new_password);
    toast.success('Password reset. You can now sign in.');
    setTimeout(() => switchTab('login'), 600);
  });

  form('verify-form', async (data) => {
    await auth.confirmEmail(lastRegistrationEmail, data.code);
    toast.success('Email verified. Redirecting…');
    setTimeout(() => { window.location.href = '/login'; }, 800);
  });

  const resendBtn = document.getElementById('resend-code-btn');
  resendBtn?.addEventListener('click', async () => {
    if (!lastRegistrationEmail) {
      toast.warning('Register first to receive a code.');
      return;
    }
    const result = await auth.resendCode(lastRegistrationEmail);
    if (result && result.code) {
      toast.info(`Dev mode: your code is ${result.code}`, { duration: 8000 });
    } else {
      toast.success('A new code has been sent.');
    }
  });
}

function form(id, handler) {
  const node = document.getElementById(id);
  if (!node) return;
  node.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submit = node.querySelector('[type="submit"]');
    const originalText = submit?.textContent;
    if (submit) {
      submit.disabled = true;
      submit.textContent = 'Please wait…';
    }
    try {
      const data = Object.fromEntries(new FormData(node).entries());
      await handler(data);
    } catch (err) {
      toast.error(err.message || 'Something went wrong');
    } finally {
      if (submit) {
        submit.disabled = false;
        submit.textContent = originalText;
      }
    }
  });
}

function showVerifyForm() {
  document.querySelectorAll('.auth-form').forEach((f) => f.classList.remove('active'));
  document.querySelector('#verify-form').classList.add('active');
}
