<script>
  import { toasts } from '../toast.js';

  function dismiss(id) {
    toasts.dismiss(id);
  }
</script>

<div class="toast-stack">
  {#each $toasts as toast (toast.id)}
    <div class="toast toast--{toast.type}">
      <div class="toast__body">
        {#if toast.title}<div class="toast__title">{toast.title}</div>{/if}
        <div class="toast__msg">{toast.message}</div>
      </div>
      <button class="toast__close" on:click={() => dismiss(toast.id)}>×</button>
    </div>
  {/each}
</div>
