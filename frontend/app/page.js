'use client';
import { useEffect, useState } from 'react';
import { api, errorText } from '@/lib/api';
import ListingCard from '@/components/ListingCard';

const PAGE_SIZE = 9;
const EMPTY = { search: '', city: '', state: '', max_price: '', bedrooms: '1', bathrooms: '1', sale_type: 'sale', home_type: 'house' };

export default function HomePage() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searching, setSearching] = useState(false);
  const [filters, setFilters] = useState(EMPTY);
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE));

  // The API paginates: { count, next, previous, results }. 404 means "nothing found".
  async function fetchPage(isSearch, f, p) {
    setLoading(true); setError('');
    const params = new URLSearchParams(isSearch ? f : {});
    params.set('page', p);
    params.set('page_size', PAGE_SIZE);
    const res = await api(`/api/listing/${isSearch ? 'search' : 'get-listings'}?${params}`);
    if (res.ok) {
      setListings(res.data.results ?? res.data.listings ?? []);
      setCount(res.data.count ?? 0);
    } else if (res.status === 404) {
      setListings([]); setCount(0);
    } else {
      setError(errorText(res));
    }
    setSearching(isSearch);
    setPage(p);
    setLoading(false);
  }

  useEffect(() => { fetchPage(false, EMPTY, 1); }, []);

  function onSearch(e) {
    e.preventDefault();
    fetchPage(true, filters, 1);
  }

  function goTo(p) {
    fetchPage(searching, filters, p);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });

  return (
    <>
      <h1>Listings</h1>
      <form className="filters" onSubmit={onSearch}>
        <label>Keyword<input required value={filters.search} onChange={set('search')} placeholder="pool, garden…" /></label>
        <label>City<input required value={filters.city} onChange={set('city')} /></label>
        <label>State<input required value={filters.state} onChange={set('state')} /></label>
        <label>Max price<input required type="number" min="0" value={filters.max_price} onChange={set('max_price')} /></label>
        <label>Min bedrooms<input required type="number" min="0" value={filters.bedrooms} onChange={set('bedrooms')} /></label>
        <label>Min bathrooms<input required type="number" min="0" step="0.5" value={filters.bathrooms} onChange={set('bathrooms')} /></label>
        <label>Sale type
          <select value={filters.sale_type} onChange={set('sale_type')}>
            <option value="sale">For sale</option><option value="rent">For rent</option>
          </select>
        </label>
        <label>Home type
          <select value={filters.home_type} onChange={set('home_type')}>
            <option value="house">House</option><option value="condo">Condo</option><option value="townhouse">Townhouse</option>
          </select>
        </label>
        <button type="submit">Search</button>
        {searching && <button type="button" className="btn-ghost" onClick={() => { setFilters(EMPTY); fetchPage(false, EMPTY, 1); }}>Clear</button>}
      </form>

      {error && <p className="error">{error}</p>}
      {loading ? <p className="muted">Loading…</p> : listings.length === 0 ? (
        <p className="muted">{searching ? 'No listings match your search.' : 'No listings published yet.'}</p>
      ) : (
        <div className="grid">{listings.map((l) => <ListingCard key={l.id} listing={l} />)}</div>
      )}

      {totalPages > 1 && (
        <div className="pager">
          <button className="btn-ghost" disabled={loading || page <= 1} onClick={() => goTo(page - 1)}>← Previous</button>
          <span className="muted">Page {page} of {totalPages}</span>
          <button className="btn-ghost" disabled={loading || page >= totalPages} onClick={() => goTo(page + 1)}>Next →</button>
        </div>
      )}
    </>
  );
}
