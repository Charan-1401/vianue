import useAuth from '../hooks/useAuth'

const dashboardTitles: Record<string, string> = {
  ADMIN: 'Admin Dashboard',
  OWNER: 'Owner Dashboard',
  VENDOR: 'Vendor Dashboard',
  CUSTOMER: 'My Bookings',
}

export default function Dashboard() {
  const { user } = useAuth()

  if (!user) return null

  const title = user.is_staff ? 'Admin Dashboard' : (dashboardTitles[user.role] || 'Dashboard')

  return (
    <section className="dashboard-page">
      <h1>{title}</h1>
      <p>Welcome back, {user.username}.</p>
      <div className="dashboard-meta">
        <span>Role: {user.role}</span>
        <span>Email: {user.email}</span>
      </div>
    </section>
  )
}
