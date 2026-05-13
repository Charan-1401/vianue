import { useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { login } from '../api/auth'
import useAuth from '../hooks/useAuth'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [status, setStatus] = useState({ message: '', tone: '' })
  const [loading, setLoading] = useState(false)
  const { loadUser } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setStatus({ message: 'Submitting request.', tone: '' })
    try {
      await login(form)
      await loadUser()
      setStatus({ message: 'Session created. Redirecting...', tone: 'success' })
      const next = searchParams.get('next') || '/dashboard'
      setTimeout(() => navigate(next, { replace: true }), 400)
    } catch (error) {
      const axiosError = error as { response?: { data?: { detail?: string } } }
      const detail = axiosError.response?.data?.detail || 'Login failed.'
      setStatus({ message: detail, tone: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="split-layout">
      <div className="panel-copy">
        <p className="eyebrow">Session</p>
        <h1>Sign in to work the platform.</h1>
        <p className="hero-text">
          Authenticated via httpOnly cookies — tokens are not accessible from JavaScript.
        </p>
      </div>
      <div className="auth-shell">
        <form className="form-card" onSubmit={handleSubmit}>
          <div className="form-head">
            <p className="eyebrow">Login</p>
            <h2>Access your account</h2>
          </div>
          <label className="field">
            <span>Username</span>
            <input type="text" name="username" autoComplete="username" required
              value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </label>
          <label className="field">
            <span>Password</span>
            <input type="password" name="password" autoComplete="current-password" required
              value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </label>
          <button className="button button-primary" type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
          {status.message && (
            <p className={`form-status ${status.tone ? `is-${status.tone}` : ''}`}>{status.message}</p>
          )}
          <p className="form-footer">
            Don't have an account? <Link to="/register">Create one</Link>
          </p>
        </form>
      </div>
    </section>
  )
}
