export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Tokens live in localStorage (fine for a learning project;
// httpOnly cookies are safer for production).
export const tokens = {
  get access() { return typeof window === 'undefined' ? null : localStorage.getItem('access'); },
  get refresh() { return typeof window === 'undefined' ? null : localStorage.getItem('refresh'); },
  set(access, refresh) {
    localStorage.setItem('access', access);
    if (refresh) localStorage.setItem('refresh', refresh);
  },
  clear() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
  },
};

async function refreshAccess() {
  if (!tokens.refresh) return false;
  const res = await fetch(`${API_URL}/api/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });
  if (!res.ok) { tokens.clear(); return false; }
  const data = await res.json();
  tokens.set(data.access, data.refresh);
  return true;
}

// Returns { ok, status, data }. Never throws on HTTP errors.
export async function api(path, { method = 'GET', body, auth = false } = {}, retried = false) {
  const headers = {};
  const isForm = typeof FormData !== 'undefined' && body instanceof FormData;
  if (body && !isForm) headers['Content-Type'] = 'application/json';
  if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
    });
  } catch {
    return { ok: false, status: 0, data: { error: 'Cannot reach the API. Is the Django server running?' } };
  }

  if (res.status === 401 && auth && !retried && (await refreshAccess())) {
    return api(path, { method, body, auth }, true);
  }

  let data = null;
  try { data = await res.json(); } catch { /* 204 or empty body */ }
  return { ok: res.ok, status: res.status, data };
}

export function errorText(res) {
  const d = res.data;
  if (!d) return `Request failed (${res.status})`;
  return d.error || d.detail || Object.values(d).flat().join(' ') || `Request failed (${res.status})`;
}

// Serializer returns relative image paths like /media/listings/x.jpg
export function imageUrl(path) {
  if (!path) return '';
  return path.startsWith('http') ? path : `${API_URL}${path}`;
}

export const money = (n) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
