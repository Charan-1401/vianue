import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <section className="split-layout">
      <div className="panel-copy">
        <p className="eyebrow">Vianue</p>
        <h1>Book Venues and Services</h1>
        <p className="hero-text">
          Find and book the perfect venue and event services for your next occasion.
        </p>
        <div className="stacked-actions">
          <Link to="/explore?kind=venues" className="button button-primary">Browse Venues</Link>
          <Link to="/explore?kind=services" className="button button-secondary">Browse Services</Link>
        </div>
      </div>
    </section>
  )
}
