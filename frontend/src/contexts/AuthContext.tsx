import { createContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { fetchMe, logout as apiLogout } from '../api/auth'
import type { User } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  setUser: (user: User | null) => void
  loadUser: () => Promise<void>
  signout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    try {
      const { data } = await fetchMe()
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const signout = async () => {
    try {
      await apiLogout()
    } catch {
      // ignore
    }
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, setUser, loadUser, signout }}>
      {children}
    </AuthContext.Provider>
  )
}
