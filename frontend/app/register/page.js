'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, errorText } from '@/lib/api';
import { useAuth } from '@/components/AuthProvider';

export default function RegisterPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ name: '', email: '', password: '', re_password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true); setError('');
    const res = await api('/auth/user/register', { method: 'POST', body: form });
    if (!res.ok) { setError(errorText(res)); setBusy(false); return; }
    const logged = await login(form.email, form.password);
    setBusy(false);
    if (logged.error) setError(logged.error); else router.push('/');
  }

  return (
    <>
      <h1>Register</h1>
      <form className="form" onSubmit={onSubmit}>
        <label>Name<input required value={form.name} onChange={set('name')} /></label>
        <label>Email<input type="email" required value={form.email} onChange={set('email')} /></label>
        <label>Password (8+ characters)<input type="password" required minLength={8} value={form.password} onChange={set('password')} /></label>
        <label>Confirm password<input type="password" required value={form.re_password} onChange={set('re_password')} /></label>
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>{busy ? 'Creating…' : 'Create account'}</button>
      </form>
    </>
  );
}
