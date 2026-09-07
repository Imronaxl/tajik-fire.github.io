import api from '../api.js';
import auth from '../auth.js';
import toast from '../components/toast.js';
import { $, $$, escapeHtml } from '../utils/helpers.js';

let tasks = [];

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.isAuthenticated()) {
    toast.warning('Sign in to manage your tasks.');
    setTimeout(() => { window.location.href = '/login?next=/tasks'; }, 800);
    return;
  }
  bindNewTask();
  bindModal();
  bindForm();
  await load();
});

async function load() {
  try {
    tasks = await api.get('/tasks/');
    render();
  } catch (err) {
    toast.error(err.message);
  }
}

function render() {
  const cols = {
    todo: tasks.filter((t) => t.status === 'todo'),
    in_progress: tasks.filter((t) => t.status === 'in_progress'),
    done: tasks.filter((t) => t.status === 'done'),
  };

  for (const status of ['todo', 'in_progress', 'done']) {
    const container = document.getElementById(`col-${status}`);
    const count = document.getElementById(`count-${status}`);
    count.textContent = cols[status].length;
    if (cols[status].length === 0) {
      container.innerHTML = '<div class="task-empty">Drop tasks here</div>';
      continue;
    }
    container.innerHTML = cols[status].map((t) => `
      <div class="task-card task-card--${t.priority}" data-id="${t.id}">
        <div class="task-card__title">${escapeHtml(t.title)}</div>
        ${t.description ? `<div class="task-card__desc">${escapeHtml(t.description)}</div>` : ''}
      </div>
    `).join('');
    $$('.task-card', container).forEach((card) => {
      card.addEventListener('click', () => openEdit(parseInt(card.dataset.id, 10)));
    });
  }
}

function bindNewTask() {
  $('#new-task-btn')?.addEventListener('click', () => openCreate());
}

function bindModal() {
  const modal = $('#task-modal');
  modal.querySelectorAll('[data-modal-close]').forEach((el) => {
    el.addEventListener('click', () => closeModal());
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });
}

function bindForm() {
  $('#task-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
      if (data.id) {
        await api.patch(`/tasks/${data.id}`, {
          title: data.title,
          description: data.description,
          status: data.status,
          priority: data.priority,
        });
        toast.success('Task updated');
      } else {
        await api.post('/tasks/', {
          title: data.title,
          description: data.description,
          status: data.status,
          priority: data.priority,
        });
        toast.success('Task created');
      }
      closeModal();
      await load();
    } catch (err) {
      toast.error(err.message);
    }
  });

  $('#task-delete-btn')?.addEventListener('click', async () => {
    const id = $('#task-form [name="id"]').value;
    if (!id) return;
    try {
      await api.delete(`/tasks/${id}`);
      toast.success('Task deleted');
      closeModal();
      await load();
    } catch (err) {
      toast.error(err.message);
    }
  });
}

function openCreate() {
  $('#task-modal-title').textContent = 'New task';
  $('#task-form').reset();
  $('#task-form [name="id"]').value = '';
  $('#task-delete-btn').style.display = 'none';
  $('#task-modal').classList.add('modal--open');
}

function openEdit(id) {
  const task = tasks.find((t) => t.id === id);
  if (!task) return;
  $('#task-modal-title').textContent = 'Edit task';
  const form = $('#task-form');
  form.elements.id.value = task.id;
  form.elements.title.value = task.title;
  form.elements.description.value = task.description || '';
  form.elements.status.value = task.status;
  form.elements.priority.value = task.priority;
  $('#task-delete-btn').style.display = '';
  $('#task-modal').classList.add('modal--open');
}

function closeModal() {
  $('#task-modal').classList.remove('modal--open');
}
