'use client';
import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api, tokens, errorText } from '@/lib/api';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    if (!tokens.access) { setUser(null); setLoading(false); return; }
    const res = await api('/auth/user/me', { auth: true });
    setUser(res.ok ? res.data.user : null);
    setLoading(false);
  }, []);

  useEffect(() => { loadUser(); }, [loadUser]);

  async function login(email, password) {
    const res = await api('/api/token/', { method: 'POST', body: { email, password } });
    if (!res.ok) return { error: res.status === 401 ? 'Wrong email or password' : errorText(res) };
    tokens.set(res.data.access, res.data.refresh);
    await loadUser();
    return {};
  }

  function logout() {
    tokens.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
