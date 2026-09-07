<script>
  import { onMount } from 'svelte';
  import api from '../../lib/api.js';
  import { user } from '../../lib/auth.js';
  import { toasts } from '../../lib/toast.js';
  import { escapeHtml } from '../../lib/utils.js';
  import { push } from '../../lib/router.js';

  let tasks = [];
  let showForm = false;
  let editingId = null;
  let form = { title: '', description: '', status: 'todo', priority: 'medium' };

  onMount(async () => {
    if (!$user) {
      toasts.warning('Войдите, чтобы управлять задачами.');
      setTimeout(() => push(`/login?next=/tasks`), 800);
      return;
    }
    await load();
  });

  async function load() {
    try {
      tasks = await api.get('/tasks/');
    } catch (err) { toasts.error(err.message); }
  }

  function openCreate() {
    editingId = null;
    form = { title: '', description: '', status: 'todo', priority: 'medium' };
    showForm = true;
  }

  function openEdit(task) {
    editingId = task.id;
    form = { title: task.title, description: task.description || '', status: task.status, priority: task.priority };
    showForm = true;
  }

  async function save() {
    try {
      if (editingId) {
        await api.patch(`/tasks/${editingId}`, form);
        toasts.success('Задача обновлена');
      } else {
        await api.post('/tasks/', form);
        toasts.success('Задача создана');
      }
      showForm = false;
      await load();
    } catch (err) { toasts.error(err.message); }
  }

  async function remove(id) {
    if (!confirm('Удалить задачу?')) return;
    try {
      await api.delete(`/tasks/${id}`);
      toasts.success('Задача удалена');
      await load();
    } catch (err) { toasts.error(err.message); }
  }

  function drop(status) {
    return async (e) => {
      e.preventDefault();
      const id = e.dataTransfer.getData('text/plain');
      if (!id) return;
      try {
        await api.patch(`/tasks/${id}`, { status });
        await load();
      } catch (err) { toasts.error(err.message); }
    };
  }

  function dragStart(e, task) {
    e.dataTransfer.setData('text/plain', String(task.id));
  }

  $: cols = {
    todo: tasks.filter((t) => t.status === 'todo'),
    in_progress: tasks.filter((t) => t.status === 'in_progress'),
    done: tasks.filter((t) => t.status === 'done'),
  };
</script>

<div class="page">
  <header class="page-header">
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <div>
        <h1>Задачи</h1>
        <p>Лёгкий трекер для учебного плана. Статус и приоритет помогают держать фокус.</p>
      </div>
      <button class="btn btn--primary btn--sm" on:click={openCreate}>+ Новая задача</button>
    </div>
  </header>

  <div class="board">
    {#each ['todo', 'in_progress', 'done'] as status}
      <div
        class="column"
        on:drop={drop(status)}
        on:dragover|preventDefault
      >
        <header>
          <h3>{status === 'todo' ? 'To do' : status === 'in_progress' ? 'В работе' : 'Готово'}</h3>
          <span class="badge">{cols[status].length}</span>
        </header>
        <div class="column__body">
          {#each cols[status] as task}
            <div
              class="task-card task-card--{task.priority}"
              draggable="true"
              on:dragstart={(e) => dragStart(e, task)}
              on:click={() => openEdit(task)}
              role="button"
              tabindex="0"
            >
              <div class="task-card__title">{task.title}</div>
              {#if task.description}<div class="task-card__desc">{task.description}</div>{/if}
            </div>
          {/each}
          {#if cols[status].length === 0}
            <div class="column__empty">Перетащите сюда задачи</div>
          {/if}
        </div>
      </div>
    {/each}
  </div>
</div>

{#if showForm}
  <div class="modal">
    <div class="modal__overlay" on:click={() => (showForm = false)} role="presentation"></div>
    <div class="modal__content modal__content--sm">
      <header class="modal__header">
        <h2 class="modal__title">{editingId ? 'Редактировать задачу' : 'Новая задача'}</h2>
        <button class="modal__close" on:click={() => (showForm = false)} aria-label="Закрыть">×</button>
      </header>
      <div class="modal__body">
        <div class="field">
          <label class="field-label" for="task-title">Заголовок</label>
          <input class="input" id="task-title" bind:value={form.title} type="text" required>
        </div>
        <div class="field">
          <label class="field-label" for="task-desc">Описание</label>
          <textarea class="textarea" id="task-desc" bind:value={form.description} rows="3"></textarea>
        </div>
        <div class="field-row">
          <div class="field">
            <label class="field-label" for="task-status">Статус</label>
            <select class="select" id="task-status" bind:value={form.status}>
              <option value="todo">To do</option>
              <option value="in_progress">В работе</option>
              <option value="done">Готово</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label" for="task-prio">Приоритет</label>
            <select class="select" id="task-prio" bind:value={form.priority}>
              <option value="low">Низкий</option>
              <option value="medium">Средний</option>
              <option value="high">Высокий</option>
            </select>
          </div>
        </div>
        <div class="flex gap-2 mt-4">
          <button class="btn btn--primary btn--block" on:click={save}>Сохранить</button>
          {#if editingId}
            <button class="btn btn--danger" on:click={() => remove(editingId)}>Удалить</button>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .board { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--sp-5); align-items: start; }
  .column { background: var(--bg-surface); border: 1px solid var(--line-1); border-radius: var(--r-lg); overflow: hidden; }
  .column header { display: flex; align-items: center; justify-content: space-between; padding: var(--sp-4) var(--sp-5); border-bottom: 1px solid var(--line-1); }
  .column header h3 { font-size: var(--fs-sm); text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-3); font-weight: 600; }
  .column__body { padding: var(--sp-3); display: flex; flex-direction: column; gap: var(--sp-3); min-height: 200px; }
  .task-card { background: var(--bg-elevated); border: 1px solid var(--line-1); border-radius: var(--r-md); padding: var(--sp-4); cursor: pointer; transition: all var(--ease); position: relative; }
  .task-card:hover { border-color: var(--line-2); transform: translateY(-1px); }
  .task-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--text-3); border-radius: var(--r-md) 0 0 var(--r-md); }
  .task-card--low::before { background: var(--teal); }
  .task-card--medium::before { background: var(--warn); }
  .task-card--high::before { background: var(--bad); }
  .task-card__title { font-weight: 500; font-size: var(--fs-sm); margin-bottom: var(--sp-1); }
  .task-card__desc { font-size: var(--fs-xs); color: var(--text-3); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .column__empty { padding: var(--sp-6); text-align: center; color: var(--text-3); font-size: var(--fs-xs); font-style: italic; }
  @media (max-width: 920px) { .board { grid-template-columns: 1fr; } }
</style>
