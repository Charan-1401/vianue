# Multimedia and Public Profiles API Documentation

## Overview
This document describes the new multimedia and public profile endpoints for venues and services in the Vianue platform.

## Venue Public Profiles

### Get Venue Profile
Retrieve a venue's complete profile with multimedia and owner information.

**Endpoint:** `GET /api/venues/{id}/profile/`

**Query Parameters:** None

**Response:**
```json
{
  "id": 1,
  "owner": 1,
  "owner_name": "John Smith",
  "owner_username": "johnsmith",
  "owner_phone": "+1234567890",
  "name": "Lakeview Hall",
  "venue_type": "Banquet Hall",
  "description": "Garden-facing hall",
  "address": "42 Celebration Road",
  "city": "Hyderabad",
  "state": "Telangana",
  "country": "India",
  "pincode": "500081",
  "lat": "17.360589",
  "lng": "78.474371",
  "capacity_min": 50,
  "capacity_max": 400,
  "base_price": "25000.00",
  "instagram_url": "https://instagram.com/lakeviewhall",
  "facebook_url": "https://facebook.com/lakeviewhall",
  "youtube_url": "https://youtube.com/@lakeviewhall",
  "website_url": "https://lakeviewhall.example.com",
  "status": "APPROVED",
  "amenities": [
    {
      "id": 1,
      "name": "Parking"
    },
    {
      "id": 2,
      "name": "Catering"
    }
  ],
  "media": [
    {
      "id": 1,
      "file": "https://example.com/media/venue_media/2026/05/08/front.jpg",
      "is_video": false,
      "description": "Front entrance",
      "created_at": "2026-05-08T10:30:00Z"
    },
    {
      "id": 2,
      "file": "https://example.com/media/venue_media/2026/05/08/walkthrough.mp4",
      "is_video": true,
      "description": "Virtual walkthrough",
      "created_at": "2026-05-08T10:31:00Z"
    }
  ]
}
```

## Service Public Profiles

### Get Service Profile
Retrieve a service listing's complete profile with multimedia and vendor information.

**Endpoint:** `GET /api/services/{id}/profile/`

**Response:**
```json
{
  "id": 1,
  "vendor": {
    "id": 1,
    "user": 5,
    "user_name": "Jane Doe",
    "user_username": "janedoe",
    "business_name": "Cinematic Productions",
    "phone": "+1987654321",
    "bio": "Professional event videography with 10+ years experience",
    "portfolio_url": "https://cinematicprod.example.com",
    "instagram_url": "https://instagram.com/cinematicteam",
    "facebook_url": "https://facebook.com/cinematicteam",
    "is_verified": true,
    "cities": ["Hyderabad", "Bangalore"],
    "listings_count": 5,
    "created_at": "2026-03-15T08:00:00Z"
  },
  "title": "Cinematic team",
  "description": "Full event coverage with drone shots",
  "category": 1,
  "pricing_model": "FIXED",
  "base_price": "1200.00",
  "min_order_value": "500.00",
  "max_guests_supported": 300,
  "instagram_url": "https://instagram.com/cinematicteam",
  "facebook_url": "https://facebook.com/cinematicteam",
  "youtube_url": "https://youtube.com/@cinematicteam",
  "website_url": "https://cinematicteam.example.com",
  "status": "APPROVED",
  "media": [
    {
      "id": 1,
      "file": "https://example.com/media/service_media/2026/05/08/portfolio.jpg",
      "is_video": false,
      "description": "Wedding ceremony highlight",
      "created_at": "2026-05-08T09:15:00Z"
    },
    {
      "id": 2,
      "file": "https://example.com/media/service_media/2026/05/08/promo.mp4",
      "is_video": true,
      "description": "Service promotional video",
      "created_at": "2026-05-08T09:16:00Z"
    }
  ],
  "packages": [
    {
      "id": 1,
      "listing": 1,
      "name": "Standard Package",
      "price": "1200.00",
      "duration_hours": 4,
      "inclusions": ["4-hour coverage", "Highlights reel", "50 edited photos"]
    }
  ],
  "addons": [
    {
      "id": 1,
      "listing": 1,
      "name": "Drone shots",
      "unit_type": "PER_UNIT",
      "unit_price": "500.00"
    }
  ],
  "created_at": "2026-04-01T12:00:00Z",
  "updated_at": "2026-05-08T09:16:00Z"
}
```

## Vendor Public Profile

### Get Vendor Profile
Retrieve a vendor's public profile with business information.

**Endpoint:** `GET /api/services/vendor-profiles/{id}/`

**Response:**
```json
{
  "id": 1,
  "user": 5,
  "user_name": "Jane Doe",
  "user_username": "janedoe",
  "business_name": "Cinematic Productions",
  "phone": "+1987654321",
  "bio": "Professional event videography with 10+ years experience",
  "portfolio_url": "https://cinematicprod.example.com",
  "instagram_url": "https://instagram.com/cinematicteam",
  "facebook_url": "https://facebook.com/cinematicteam",
  "is_verified": true,
  "cities": ["Hyderabad", "Bangalore"],
  "listings_count": 5,
  "created_at": "2026-03-15T08:00:00Z"
}
```

## Uploaded Media Management

### Upload Venue Media
Owners can upload photos and videos when creating or updating venues.

**Endpoint:** `POST /api/venues/owner/` (create) or `PUT /api/venues/owner/{id}/` (update)

**Request (multipart/form-data):**
```
name: Lakeview Hall
venue_type: Banquet Hall
description: Garden-facing hall
address: 42 Celebration Road
city: Hyderabad
media_uploads: [file1.jpg, file2.mp4]
```

**File Support:**
- **Images:** JPG, PNG, GIF, WebP
- **Videos:** MP4, WebM, MOV, MKV, AVI, MPEG
- **Max file size:** 100MB per file
- **Auto-detection:** System automatically detects video vs image

### Upload Service Media
Vendors can upload photos and videos for service listings.

**Endpoint:** `POST /api/services/vendor/` (create) or `PUT /api/services/vendor/{id}/` (update)

**Request (multipart/form-data):**
```
title: Cinematic team
description: Full event coverage
pricing_model: FIXED
base_price: 1200.00
media_uploads: [portfolio.jpg, promo.mp4]
```

### Delete Media
Delete a specific media file from a venue or service.

**Endpoint:** `DELETE /api/venues/owner/{venue_id}/media/{media_id}/`
**Endpoint:** `DELETE /api/services/vendor/{service_id}/media/{media_id}/`

## Media File Fields

All media objects now include:

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Media item ID |
| file | string | URL to the media file |
| is_video | boolean | Whether the media is a video |
| description | string | Optional description of the media |
| created_at | datetime | When the media was uploaded |

## Vendor Profile Enhancements

Vendor profiles now include:

| Field | Type | Description |
|-------|------|-------------|
| bio | string | Business description |
| portfolio_url | string | Link to vendor's portfolio website |
| instagram_url | string | Instagram profile URL |
| facebook_url | string | Facebook page URL |
| is_verified | boolean | Verification status (read-only) |
| listings_count | integer | Number of approved listings |
| created_at | datetime | Profile creation date |

## Venue Profile Enhancements

Venue listings now include owner contact information:

| Field | Type | Description |
|-------|------|-------------|
| owner_name | string | Owner's full name |
| owner_username | string | Owner's username |
| owner_phone | string | Owner's phone number |

## Database Optimization

The following indexes have been added for improved query performance:

**Venues:**
- `venue_status_created_idx`: Status + creation date (quick listing lookup)
- `venuemedia_created_idx`: Venue media by creation date (recent media fetch)

**Services:**
- `svc_status_created_idx`: Service status + creation date (quick listing lookup)
- `svcmedia_created_idx`: Service media by creation date (recent media fetch)
- `vendor_verified_idx`: Vendor verification status + creation date (verified vendor lookup)

## Media Upload Paths

All uploaded media is organized by date in storage:

- Venue media: `venue_media/YYYY/MM/DD/filename`
- Service media: `service_media/YYYY/MM/DD/filename`

This organization facilitates easy backup and archival of media by date.

## Availability Check Remains Unchanged

The existing availability endpoint continues to work for checking venue availability:

**Endpoint:** `GET /api/venues/{id}/availability/?start_at=2026-05-15T10:00:00Z&end_at=2026-05-15T18:00:00Z`

## Testing

Run the test suite to validate all multimedia and profile features:

```bash
python manage.py test services.tests_vendor venues.tests_owner -v 2
```

Test coverage includes:
- Media upload and file type detection
- Public profile endpoint access
- Vendor profile exposure
- Media metadata (description, timestamps)
- Owner contact information visibility
