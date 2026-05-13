import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../api/auth'

export default function Register() {
  const [form, setForm] = useState({
    username: '', email: '', phone: '', role: 'CUSTOMER', password: '',
  })
  const [status, setStatus] = useState({ message: '', tone: '' })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setStatus({ message: 'Submitting request.', tone: '' })
    try {
      await register(form)
      setStatus({ message: 'Account created. Redirecting to login.', tone: 'success' })
      setTimeout(() => navigate('/login?registered=1'), 700)
    } catch (error) {
      const axiosError = error as { response?: { data?: Record<string, unknown> } }
      const data = axiosError.response?.data || {}
      const first = Object.values(data).flat()[0]
      setStatus({ message: String(first || 'Registration failed.'), tone: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="split-layout">
      <div className="panel-copy">
        <p className="eyebrow">Account onboarding</p>
        <h1>Create a Vianue user profile.</h1>
        <p className="hero-text">
          The registration form posts directly to /api/auth/register.
        </p>
      </div>
      <div className="auth-shell">
        <form className="form-card" onSubmit={handleSubmit}>
          <div className="form-head">
            <p className="eyebrow">Register</p>
            <h2>Open a new account</h2>
          </div>
          <label className="field">
            <span>Username</span>
            <input type="text" name="username" autoComplete="username" required
              value={form.username} onChange={handleChange} />
          </label>
          <label className="field">
            <span>Email</span>
            <input type="email" name="email" autoComplete="email" required
              value={form.email} onChange={handleChange} />
          </label>
          <label className="field">
            <span>Phone</span>
            <input type="tel" name="phone" autoComplete="tel"
              value={form.phone} onChange={handleChange} />
          </label>
          <label className="field">
            <span>Role</span>
            <select name="role" value={form.role} onChange={handleChange} required>
              <option value="CUSTOMER">Customer</option>
              <option value="OWNER">Owner</option>
              <option value="VENDOR">Vendor</option>
              <option value="ADMIN">Admin</option>
            </select>
          </label>
          <label className="field">
            <span>Password</span>
            <input type="password" name="password" autoComplete="new-password" required
              value={form.password} onChange={handleChange} />
          </label>
          <button className="button button-primary" type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create account'}
          </button>
          {status.message && (
            <p className={`form-status ${status.tone ? `is-${status.tone}` : ''}`}>{status.message}</p>
          )}
          <p className="form-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </form>
      </div>
    </section>
  )
}
