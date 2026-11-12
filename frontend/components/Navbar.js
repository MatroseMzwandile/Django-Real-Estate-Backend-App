'use client';
import Link from 'next/link';
import { useAuth } from './AuthProvider';

export default function Navbar() {
  const { user, loading, logout } = useAuth();
  return (
    <nav className="nav">
      <Link href="/" className="brand">Real Estate</Link>
      <div className="nav-links">
        {!loading && user && (
          <>
            {user.is_realtor && <Link href="/dashboard">Dashboard</Link>}
            <span className="muted">{user.name}</span>
            <button className="link-btn" onClick={logout}>Log out</button>
          </>
        )}
        {!loading && !user && (
          <>
            <Link href="/login">Log in</Link>
            <Link href="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
