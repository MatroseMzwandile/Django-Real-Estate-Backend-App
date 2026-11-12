'use client';
import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api, errorText, imageUrl, money } from '@/lib/api';
import { useAuth } from '@/components/AuthProvider';

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const res = await api('/api/listing/manage', { auth: true });
    if (res.ok) setListings(res.data.listing); else setError(errorText(res));
    setLoading(false);
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.replace('/login'); return; }
    if (user.is_realtor) load(); else setLoading(false);
  }, [authLoading, user, router, load]);

  async function togglePublish(l) {
    const res = await api('/api/listing/manage', {
      method: 'PATCH', auth: true,
      body: { slug: l.slug, is_published: l.is_published ? 'False' : 'True' },
    });
    if (res.ok) load(); else setError(errorText(res));
  }

  async function remove(l) {
    if (!confirm(`Delete "${l.title}"? This cannot be undone.`)) return;
    const res = await api('/api/listing/manage', { method: 'DELETE', auth: true, body: { slug: l.slug } });
    if (res.ok) load(); else setError(errorText(res));
  }

  if (authLoading || !user) return <p className="muted">Loading…</p>;
  if (!user.is_realtor) {
    return <p>This area is for realtor accounts only. Ask an admin to enable <code>is_realtor</code> on your account.</p>;
  }

  return (
    <>
      <div className="head">
        <h1>My listings</h1>
        <Link href="/dashboard/new" className="btn">+ New listing</Link>
      </div>
      {error && <p className="error">{error}</p>}
      {loading ? <p className="muted">Loading…</p> : listings.length === 0 ? (
        <p className="muted">You have no listings yet.</p>
      ) : listings.map((l) => (
        <div className="dash-row" key={l.id}>
          <img src={imageUrl(l.main_photo)} alt="" />
          <div className="info">
            <strong>{l.title}</strong>
            <div className="muted">{money(l.price)} · {l.city} · {l.is_published ? 'Published' : 'Draft'}</div>
          </div>
          {l.is_published && <Link href={`/listings/${l.slug}`}>View</Link>}
          <button className="btn-ghost" onClick={() => togglePublish(l)}>{l.is_published ? 'Unpublish' : 'Publish'}</button>
          <button className="btn-danger" onClick={() => remove(l)}>Delete</button>
        </div>
      ))}
    </>
  );
}
