<script>
  import { onMount } from 'svelte';
  import { push } from '../../lib/router.js';
  import api from '../../lib/api.js';
  import { user, updateProfile, changePassword } from '../../lib/auth.js';
  import { toasts } from '../../lib/toast.js';
  import { initials, relativeTime, verdictClass, verdictLabel, languageLabel } from '../../lib/utils.js';
  import { t } from '../../core/i18n/index.js';

  let stats = null;
  let submissions = [];
  let showEdit = false;
  let editForm = { first_name: '', last_name: '' };
  let pwdForm = { old_password: '', new_password: '' };

  onMount(async () => {
    if (!$user) {
      toasts.warning($t('toast.loginRequired'));
      setTimeout(() => push('/login?next=/profile'), 800);
      return;
    }
    editForm.first_name = $user.first_name || '';
    editForm.last_name = $user.last_name || '';
    try {
      stats = await api.get('/stats/me');
      submissions = await api.get('/problems/submissions', { user_id: $user.id, limit: 10 });
    } catch (_) { }
  });

  async function saveProfile() {
    try {
      await updateProfile({
        first_name: editForm.first_name || null,
        last_name: editForm.last_name || null,
      });
      toasts.success($t('profile.toast.updated'));
      showEdit = false;
    } catch (err) { toasts.error(err.message); }
  }

  async function changePwd() {
    try {
      await changePassword(pwdForm.old_password, pwdForm.new_password);
      toasts.success($t('profile.toast.passwordUpdated'));
      pwdForm = { old_password: '', new_password: '' };
    } catch (err) { toasts.error(err.message); }
  }
</script>

<div class="page">
  {#if $user}
    <div class="profile-header">
      <div class="avatar avatar--lg avatar--gradient" style="width:84px;height:84px;font-size:var(--fs-2xl);">{initials($user.username)}</div>
      <div class="profile-header__info">
        <div class="flex items-center gap-2 flex-wrap mb-2">
          <h1>{$user.username}</h1>
          <span class="badge badge--brand">{$user.rating || 0} {$t('leaderboard.points')}</span>
        </div>
        <p class="text-2">{$user.first_name} {$user.last_name}</p>
        <p class="text-3 text-sm mt-2">{$t('profile.joined', { date: new Date($user.created_at).toLocaleDateString('ru-RU') })}</p>
      </div>
      <div class="profile-header__actions">
        <button class="btn btn--secondary btn--sm" on:click={() => (showEdit = true)}>{$t('profile.edit')}</button>
      </div>
    </div>

    <div class="grid grid--4 mb-8">
      <div class="stat-card">
        <div class="stat-card__label">{$t('profile.stat.solved')}</div>
        <div class="stat-card__value">{stats?.solved_count ?? $user.solved_count}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">{$t('profile.stat.submissions')}</div>
        <div class="stat-card__value">{stats?.submissions_count ?? 0}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">{$t('profile.stat.accepted')}</div>
        <div class="stat-card__value">{stats?.accepted_count ?? 0}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">{$t('profile.stat.successRate')}</div>
        <div class="stat-card__value">{(stats?.success_rate ?? 0).toFixed(0)}%</div>
      </div>
    </div>

    <div class="grid grid--2">
      <div>
        <div class="section-header"><h2>{$t('profile.recent')}</h2></div>
        <div class="feed-list">
          {#if submissions.length === 0}
            <div class="empty-state">
              <h3>{$t('profile.recent.empty')}</h3>
              <p>{$t('profile.recent.empty.desc')}</p>
              <button class="btn btn--primary btn--sm mt-4" on:click={() => push('/problems')}>{$t('profile.btn.solveProblem')}</button>
            </div>
          {:else}
            {#each submissions as s}
              <a class="feed-row" href={`/problems/${s.problem_id}`} on:click|preventDefault={() => push(`/problems/${s.problem_id}`)}>
                <div class="feed-row__user"><span class="lang-badge">{languageLabel(s.language)}</span></div>
                <div class="feed-row__main">
                  <strong>{$t('submissions.title')} #{s.id}</strong>
                  <span>{$t('problems.title')} #{s.problem_id}</span>
                </div>
                <div class="feed-row__meta">
                  <span class={verdictClass(s.verdict)}>{verdictLabel(s.verdict, $t)}</span>
                  <span>{relativeTime(new Date(s.created_at))}</span>
                </div>
              </a>
            {/each}
          {/if}
        </div>
      </div>
      <div>
        <div class="section-header"><h2>{$t('profile.settings')}</h2></div>
        <div class="card">
          <div class="card__body">
            <form on:submit|preventDefault={changePwd}>
              <div class="field">
                <label class="field-label" for="cp-old">{$t('profile.field.oldPassword')}</label>
                <input class="input" id="cp-old" type="password" bind:value={pwdForm.old_password} required>
              </div>
              <div class="field">
                <label class="field-label" for="cp-new">{$t('profile.field.newPassword')}</label>
                <input class="input" id="cp-new" type="password" bind:value={pwdForm.new_password} required>
                <p class="field-hint">{$t('auth.hint.password')}</p>
              </div>
              <button type="submit" class="btn btn--primary btn--block">{$t('profile.btnUpdatePassword')}</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

{#if showEdit}
  <div class="modal">
    <div class="modal__overlay" on:click={() => (showEdit = false)} role="presentation"></div>
    <div class="modal__content modal__content--sm">
      <header class="modal__header">
        <h2 class="modal__title">{$t('profile.modal.editTitle')}</h2>
        <button class="modal__close" on:click={() => (showEdit = false)} aria-label={$t('common.close')}>×</button>
      </header>
      <div class="modal__body">
        <div class="field-row">
          <div class="field">
            <label class="field-label" for="edit-first">{$t('auth.field.firstName')}</label>
            <input class="input" id="edit-first" bind:value={editForm.first_name} type="text">
          </div>
          <div class="field">
            <label class="field-label" for="edit-last">{$t('auth.field.lastName')}</label>
            <input class="input" id="edit-last" bind:value={editForm.last_name} type="text">
          </div>
        </div>
        <button class="btn btn--primary btn--block" on:click={saveProfile}>{$t('profile.btnSave')}</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .profile-header {
    display: grid; grid-template-columns: auto 1fr auto; gap: var(--sp-6);
    align-items: center; margin-bottom: var(--sp-8); padding: var(--sp-6);
    background: var(--bg-surface); border: 1px solid var(--line-1);
    border-radius: var(--r-xl);
  }
  .profile-header__info h1 { font-size: var(--fs-2xl); letter-spacing: -0.02em; }
  @media (max-width: 720px) {
    .profile-header { grid-template-columns: auto 1fr; text-align: center; }
    .profile-header__actions { grid-column: 1 / -1; }
  }

  .feed-list { background: var(--bg-surface); border: 1px solid var(--line-1); border-radius: var(--r-lg); overflow: hidden; }
  .feed-row {
    display: grid; grid-template-columns: auto 1fr auto; gap: var(--sp-4);
    padding: var(--sp-4) var(--sp-5); border-bottom: 1px solid var(--line-1);
    align-items: center; transition: background var(--ease); color: inherit;
  }
  .feed-row:last-child { border-bottom: none; }
  .feed-row:hover { background: var(--bg-elevated); }
  .feed-row__user { display: flex; align-items: center; gap: var(--sp-2); min-width: 100px; }
  .feed-row__main { display: flex; flex-direction: column; min-width: 0; }
  .feed-row__main strong { font-weight: 500; font-size: var(--fs-sm); }
  .feed-row__main span { font-size: var(--fs-xs); color: var(--text-3); }
  .feed-row__meta { display: flex; align-items: center; gap: var(--sp-3); font-size: var(--fs-xs); color: var(--text-3); }
  .lang-badge { font-family: 'JetBrains Mono', monospace; font-size: var(--fs-xs); font-weight: 500; padding: 2px 6px; background: var(--bg-elevated); border-radius: var(--r-sm); color: var(--text-2); }
</style>
