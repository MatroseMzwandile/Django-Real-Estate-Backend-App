'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/components/AuthProvider';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true); setError('');
    const res = await login(form.email, form.password);
    setBusy(false);
    if (res.error) setError(res.error);
    else router.push('/');
  }

  return (
    <>
      <h1>Log in</h1>
      <form className="form" onSubmit={onSubmit}>
        <label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
        <label>Password<input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
        <p className="muted">No account? <Link href="/register">Register</Link></p>
      </form>
    </>
  );
}
