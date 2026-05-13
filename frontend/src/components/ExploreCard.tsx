import { Link } from 'react-router-dom'

interface CardProps {
  kind: 'venue' | 'service'
  id: number
  title: string
  typeLabel: string
  icon: string
  description: string
  priceDisplay: string
  priceUnit: string
  tags: string[]
  href: string
  img: string | null
  vendorName?: string
}

export default function ExploreCard({
  kind, title, typeLabel, icon, description,
  priceDisplay, priceUnit, tags, href, img, vendorName,
}: CardProps) {
  return (
    <Link to={href} className="explore-card">
      {img && (
        <div className="explore-card-img">
          <img src={img} alt={title} />
        </div>
      )}
      <div className="explore-card-body">
        <div className="explore-card-header">
          <span className="explore-card-icon">
            <i className={`fas ${icon}`} />
          </span>
          <span className="explore-card-label">{typeLabel}</span>
        </div>
        <h3 className="explore-card-title">{title}</h3>
        {vendorName && <p className="explore-card-vendor">{vendorName}</p>}
        <p className="explore-card-desc">{description}</p>
        <div className="explore-card-tags">
          {tags.map((tag) => (
            <span key={tag} className="explore-card-tag">{tag}</span>
          ))}
        </div>
        <div className="explore-card-footer">
          <span className="explore-card-price">
            &#8377;{priceDisplay}
            <small>{priceUnit}</small>
          </span>
          <span className="explore-card-cta">{kind === 'venue' ? 'Book now' : 'Book now'}</span>
        </div>
      </div>
    </Link>
  )
}
