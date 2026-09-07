export function push(path) {
  if (typeof window === 'undefined' || typeof window.navigate !== 'function') {
    window.location.href = path;
    return;
  }
  window.navigate(path);
}

export const location = typeof window !== 'undefined' ? window.location : { pathname: '/', search: '', hash: '' };
