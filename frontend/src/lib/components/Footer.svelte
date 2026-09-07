<script>
  import { version } from '../stores.js';
</script>

<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <div class="brand__logo" style="width:28px;height:28px;font-size:13px">T</div>
        <div>
          <strong>tajik-fire</strong>
          <span>v{version}</span>
        </div>
      </div>
      <nav class="footer__nav">
        <a href="/problems">Задачи</a>
        <a href="/olympiads">Контесты</a>
        <a href="/learning">Обучение</a>
        <a href="/leaderboard">Рейтинг</a>
        <a href="/docs" target="_blank">API</a>
      </nav>
      <p class="footer__note">Портфолио-проект на FastAPI + Svelte. Песочница для Python, C++ и Java, учебные треки и социальная лента.</p>
    </div>
  </div>
</footer>

<style>
  .footer {
    border-top: 1px solid var(--line-1);
    padding: var(--sp-10) 0 var(--sp-8);
    margin-top: var(--sp-16);
    background: var(--bg);
  }
  .footer__grid {
    display: grid; grid-template-columns: auto 1fr auto;
    gap: var(--sp-8); align-items: center;
  }
  .footer__brand { display: flex; align-items: center; gap: var(--sp-3); font-size: var(--fs-sm); }
  .footer__brand strong { display: block; }
  .footer__brand span { font-size: 11px; color: var(--text-3); letter-spacing: 0.04em; }
  .footer__nav { display: flex; gap: var(--sp-5); flex-wrap: wrap; font-size: var(--fs-sm); }
  .footer__nav a { color: var(--text-2); transition: color var(--ease); }
  .footer__nav a:hover { color: var(--text-1); }
  .footer__note {
    font-size: var(--fs-xs); color: var(--text-3); max-width: 36ch;
    text-align: right; line-height: 1.5;
  }
  @media (max-width: 760px) {
    .footer__grid { grid-template-columns: 1fr; text-align: center; }
    .footer__note { text-align: center; }
    .footer__nav { justify-content: center; }
    .footer__brand { justify-content: center; }
  }
</style>
