'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, errorText } from '@/lib/api';
import { useAuth } from '@/components/AuthProvider';

const slugify = (s) => s.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

export default function NewListingPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!authLoading && (!user || !user.is_realtor)) router.replace('/dashboard');
  }, [authLoading, user, router]);

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true); setError('');
    const fd = new FormData(e.currentTarget);
    if (!fd.get('slug')) fd.set('slug', slugify(fd.get('title')));
    const res = await api('/api/listing/manage', { method: 'POST', auth: true, body: fd });
    setBusy(false);
    if (res.ok) router.push('/dashboard'); else setError(errorText(res));
  }

  return (
    <>
      <h1>New listing</h1>
      <form className="form" onSubmit={onSubmit}>
        <label>Title<input name="title" required maxLength={100} /></label>
        <label>Slug (optional, made from the title if empty)<input name="slug" pattern="[a-z0-9-]*" /></label>
        <label>Address<input name="address" required /></label>
        <div className="row">
          <label>City<input name="city" required /></label>
          <label>State<input name="state" required /></label>
        </div>
        <label>Zip code (max 5 characters)<input name="zipcode" required maxLength={5} /></label>
        <label>Description<textarea name="description" rows={5} required /></label>
        <div className="row">
          <label>Price<input name="price" type="number" min="0" required /></label>
          <label>Bedrooms<input name="bedrooms" type="number" min="0" required /></label>
        </div>
        <div className="row">
          <label>Bathrooms<input name="bathrooms" type="number" min="0.5" max="9.5" step="0.5" required /></label>
          <label>Sale type
            <select name="sale_type"><option value="FOR_SALE">For sale</option><option value="FOR_RENT">For rent</option></select>
          </label>
        </div>
        <label>Home type
          <select name="home_type"><option value="HOUSE">House</option><option value="CONDO">Condo</option><option value="TOWNHOUSE">Townhouse</option></select>
        </label>
        <label>Main photo<input name="main_photo" type="file" accept="image/*" required /></label>
        <label>Photo 1<input name="photo_1" type="file" accept="image/*" required /></label>
        <label>Photo 2<input name="photo_2" type="file" accept="image/*" required /></label>
        <label>Photo 3<input name="photo_3" type="file" accept="image/*" required /></label>
        <label>Visibility
          <select name="is_published"><option value="False">Draft</option><option value="True">Published</option></select>
        </label>
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>{busy ? 'Saving…' : 'Create listing'}</button>
      </form>
    </>
  );
}
