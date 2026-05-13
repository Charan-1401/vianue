import { Link, Outlet } from 'react-router-dom'
import useAuth from '../hooks/useAuth'

export default function Layout() {
  const { user, signout } = useAuth()

  return (
    <div className="page-shell">
      <header className="site-header">
        <Link to="/" className="brand">
          <span className="brand-mark">V</span>
          <span className="brand-copy">
            <strong>Vianue</strong>
            <small>Venue and event service booking</small>
          </span>
        </Link>
        <nav className="site-nav" aria-label="Primary">
          <Link to="/explore?kind=venues">Venues</Link>
          <Link to="/explore?kind=services">Services</Link>
        </nav>
        <div className="site-actions">
          {user ? (
            <>
              <Link to="/dashboard" className="button button-secondary">Dashboard</Link>
              <button onClick={signout} className="button button-secondary">Sign out</button>
            </>
          ) : (
            <>
              <Link to="/login" className="button button-secondary">Sign in</Link>
              <Link to="/register" className="button button-primary">List your space</Link>
            </>
          )}
        </div>
      </header>
      <main className="page-main">
        <Outlet />
      </main>
    </div>
  )
}
