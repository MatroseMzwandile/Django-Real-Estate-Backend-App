import Link from 'next/link';
import { imageUrl, money } from '@/lib/api';

export default function ListingCard({ listing }) {
  return (
    <Link href={`/listings/${listing.slug}`} className="card">
      <img src={imageUrl(listing.main_photo)} alt={listing.title} />
      <div className="card-body">
        <span className="tag">{listing.sale_type}</span>
        <h3>{listing.title}</h3>
        <p className="price">{money(listing.price)}</p>
        <p className="muted">{listing.city}, {listing.state}</p>
        <p className="muted">{listing.bedrooms} bd · {listing.bathrooms} ba · {listing.home_type}</p>
      </div>
    </Link>
  );
}
