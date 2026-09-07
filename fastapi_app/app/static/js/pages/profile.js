import api from '../api.js';
import auth from '../auth.js';
import toast from '../components/toast.js';
import {
  $, escapeHtml, initials, relativeTime, verdictClass, verdictLabel, languageLabel,
} from '../utils/helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
  bindEditModal();
  bindPasswordForm();
  await loadProfile();
  await loadRecent();
});

async function loadProfile() {
  const user = auth.getUser();
  if (!user) {
    toast.warning('Please sign in to view your profile.');
    setTimeout(() => { window.location.href = '/login?next=/profile'; }, 800);
    return;
  }
  $('#profile-username').textContent = user.username;
  $('#profile-fullname').textContent = [user.first_name, user.last_name].filter(Boolean).join(' ') || 'No name set';
  $('#profile-meta').textContent = `Joined ${new Date(user.created_at).toLocaleDateString()}`;
  $('#profile-rating').textContent = `${user.rating || 0} rating`;
  const avatar = $('#profile-avatar');
  avatar.textContent = initials(user.username || 'U');
  avatar.classList.add('avatar--gradient');

  $('#edit-first').value = user.first_name || '';
  $('#edit-last').value = user.last_name || '';

  try {
    const stats = await api.get('/stats/me');
    $('#stat-solved').textContent = stats.solved_count ?? 0;
    $('#stat-submissions').textContent = stats.submissions_count ?? 0;
    $('#stat-accepted').textContent = stats.accepted_count ?? 0;
    $('#stat-rate').textContent = `${(stats.success_rate || 0).toFixed(0)}%`;
  } catch (_) { }
}

async function loadRecent() {
  const wrap = $('#profile-feed');
  try {
    const user = auth.getUser();
    if (!user) return;
    const items = await api.get('/problems/submissions', { user_id: user.id, limit: 10 });
    if (!items || items.length === 0) {
      wrap.innerHTML = `
        <div class="feed-empty">
          <h3>No submissions yet</h3>
          <p>Your recent attempts will appear here.</p>
          <a href="/problems" class="btn btn--primary btn--sm mt-4">Solve a problem</a>
        </div>`;
      return;
    }
    wrap.innerHTML = items.map((s) => `
      <a class="feed-row" href="/problems/${s.problem_id}">
        <div class="feed-row__user">
          <span class="lang-badge">${languageLabel(s.language)}</span>
        </div>
        <div class="feed-row__main">
          <strong>Submission #${s.id}</strong>
          <span>Problem #${s.problem_id}</span>
        </div>
        <div class="feed-row__meta">
          <span class="${verdictClass(s.verdict)}">${verdictLabel(s.verdict)}</span>
          <span>${relativeTime(new Date(s.created_at))}</span>
        </div>
      </a>
    `).join('');
  } catch (err) {
    wrap.innerHTML = `<div class="feed-empty"><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function bindEditModal() {
  const modal = $('#edit-modal');
  $('#profile-edit-btn')?.addEventListener('click', () => {
    modal.classList.add('modal--open');
    modal.setAttribute('aria-hidden', 'false');
  });

  modal.querySelectorAll('[data-modal-close]').forEach((el) => {
    el.addEventListener('click', () => {
      modal.classList.remove('modal--open');
      modal.setAttribute('aria-hidden', 'true');
    });
  });

  $('#edit-profile-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
      await auth.updateProfile({
        first_name: data.first_name || null,
        last_name: data.last_name || null,
      });
      toast.success('Profile updated');
      modal.classList.remove('modal--open');
      loadProfile();
    } catch (err) {
      toast.error(err.message);
    }
  });
}

function bindPasswordForm() {
  $('#change-password-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
      await auth.changePassword(data.old_password, data.new_password);
      toast.success('Password updated');
      e.target.reset();
    } catch (err) {
      toast.error(err.message);
    }
  });
}
