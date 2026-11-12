'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api, errorText, imageUrl, money } from '@/lib/api';
import { useAuth } from '@/components/AuthProvider';

export default function ListingDetailPage() {
  const { slug } = useParams();
  const { user, loading: authLoading } = useAuth();
  const [listing, setListing] = useState(null);
  const [error, setError] = useState('');
  const [active, setActive] = useState(0);

  useEffect(() => {
    if (authLoading || !user) return;
    (async () => {
      const res = await api(`/api/listing/detail?slug=${encodeURIComponent(slug)}`, { auth: true });
      if (res.ok) setListing(res.data.listing);
      else setError(errorText(res));
    })();
  }, [slug, user, authLoading]);

  if (authLoading) return <p className="muted">Loading…</p>;
  if (!user) {
    return <p>The API only shows listing details to logged-in users. <Link href="/login">Log in</Link> or <Link href="/register">register</Link> to continue.</p>;
  }
  if (error) return <p className="error">{error}</p>;
  if (!listing) return <p className="muted">Loading…</p>;

  const photos = [listing.main_photo, listing.photo_1, listing.photo_2, listing.photo_3].filter(Boolean).map(imageUrl);

  return (
    <>
      <Link href="/">← All listings</Link>
      <h1>{listing.title}</h1>
      <p className="muted">{listing.address}, {listing.city}, {listing.state} {listing.zipcode}</p>
      <img className="detail-main" src={photos[active]} alt={listing.title} />
      <div className="thumbs">
        {photos.map((src, i) => (
          <img key={src} src={src} alt="" className={i === active ? 'active' : ''} onClick={() => setActive(i)} />
        ))}
      </div>
      <p><span className="tag">{listing.sale_type}</span> <strong className="price">{money(listing.price)}</strong></p>
      <p>{listing.bedrooms} bedrooms · {listing.bathrooms} bathrooms · {listing.home_type}</p>
      <p style={{ whiteSpace: 'pre-wrap' }}>{listing.description}</p>
      <p className="muted">Listed by {listing.realtor} on {new Date(listing.date_created).toLocaleDateString()}</p>
    </>
  );
}
