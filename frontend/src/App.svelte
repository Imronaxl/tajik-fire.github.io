<script>
  import { onMount, onDestroy } from 'svelte';
  import { initAuth, user, ready } from './lib/auth.js';
  import { toasts } from './lib/toast.js';

  import Navbar from './lib/components/Navbar.svelte';
  import Footer from './lib/components/Footer.svelte';
  import ToastStack from './lib/components/ToastStack.svelte';

  import Home from './routes/pages/Home.svelte';
  import Auth from './routes/pages/Auth.svelte';
  import Problems from './routes/pages/Problems.svelte';
  import ProblemDetail from './routes/pages/ProblemDetail.svelte';
  import ProblemEditor from './routes/pages/ProblemEditor.svelte';
  import Contests from './routes/pages/Contests.svelte';
  import Leaderboard from './routes/pages/Leaderboard.svelte';
  import Submissions from './routes/pages/Submissions.svelte';
  import Learning from './routes/pages/Learning.svelte';
  import LearningDetail from './routes/pages/LearningDetail.svelte';
  import Tasks from './routes/pages/Tasks.svelte';
  import Messenger from './routes/pages/Messenger.svelte';
  import News from './routes/pages/News.svelte';
  import Profile from './routes/pages/Profile.svelte';
  import NotFound from './routes/pages/NotFound.svelte';

  let currentPath = typeof location !== 'undefined' ? location.pathname : '/';

  function handlePop() {
    currentPath = location.pathname;
    window.scrollTo(0, 0);
  }

  onMount(() => {
    initAuth();
    window.addEventListener('popstate', handlePop);
    window.addEventListener('pushstate', handlePop);
    window.addEventListener('unhandledrejection', (e) => {
      if (e.reason?.status === 401) return;
      toasts.error(e.reason?.message || 'Сетевая ошибка');
    });
  });

  onDestroy(() => {
    window.removeEventListener('popstate', handlePop);
    window.removeEventListener('pushstate', handlePop);
  });

  export function navigate(path) {
    if (path !== currentPath) {
      history.pushState({}, '', path);
      currentPath = path;
      window.dispatchEvent(new CustomEvent('pushstate', { detail: path }));
      window.scrollTo(0, 0);
    }
  }

  window.navigate = navigate;

  function match(path) {
    const parts = path.split('/').filter(Boolean);
    if (parts.length === 0) return { component: Home, params: {} };
    if (parts[0] === 'login' || parts[0] === 'register' || parts[0] === 'auth') return { component: Auth, params: { mode: parts[0] } };
    if (parts[0] === 'problems') {
      if (parts.length === 1) return { component: Problems, params: {} };
      if (parts.length === 2) return { component: ProblemDetail, params: { id: parts[1] } };
      if (parts.length === 3 && parts[2] === 'solve') return { component: ProblemEditor, params: { id: parts[1] } };
    }
    if (parts[0] === 'olympiads' || parts[0] === 'contests') return { component: Contests, params: {} };
    if (parts[0] === 'leaderboard') return { component: Leaderboard, params: {} };
    if (parts[0] === 'submissions') return { component: Submissions, params: {} };
    if (parts[0] === 'learning') {
      if (parts.length === 1) return { component: Learning, params: {} };
      return { component: LearningDetail, params: { slug: parts[1] } };
    }
    if (parts[0] === 'tasks') return { component: Tasks, params: {} };
    if (parts[0] === 'messenger') return { component: Messenger, params: {} };
    if (parts[0] === 'news') return { component: News, params: {} };
    if (parts[0] === 'profile') return { component: Profile, params: {} };
    return { component: NotFound, params: {} };
  }

  $: route = match(currentPath);
  $: CurrentComponent = route.component;
  $: params = route.params;
</script>

<Navbar />
<main>
  {#if $ready}
    <svelte:component this={CurrentComponent} {params} />
  {:else}
    <div class="page empty-state">
      <div class="spinner"></div>
      <p>Загрузка…</p>
    </div>
  {/if}
</main>
<Footer />
<ToastStack />

<style>
  main { flex: 1; display: flex; flex-direction: column; }
</style>

