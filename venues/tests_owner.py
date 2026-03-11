import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from accounts.models import User
from venues.models import Venue


class OwnerVenueDashboardTests(APITestCase):
    def setUp(self):
        self.temp_media_root = tempfile.TemporaryDirectory()
        self.original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.temp_media_root.name
        self.addCleanup(self.cleanup_media_root)

        self.owner = User.objects.create(username='owner1', role='OWNER')
        self.client.force_authenticate(user=self.owner)

    def cleanup_media_root(self):
        settings.MEDIA_ROOT = self.original_media_root
        self.temp_media_root.cleanup()

    def test_owner_can_upload_media_and_social_links(self):
        photo = SimpleUploadedFile('front.jpg', b'photo-bytes', content_type='image/jpeg')
        video = SimpleUploadedFile('walkthrough.mp4', b'video-bytes', content_type='video/mp4')

        response = self.client.post(
            '/api/venues/owner/',
            {
                'name': 'Lakeview Hall',
                'venue_type': 'Banquet Hall',
                'description': 'Garden-facing hall',
                'address': '42 Celebration Road',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'country': 'India',
                'pincode': '500081',
                'capacity_min': '50',
                'capacity_max': '400',
                'base_price': '25000.00',
                'instagram_url': 'https://instagram.com/lakeviewhall',
                'facebook_url': 'https://facebook.com/lakeviewhall',
                'youtube_url': 'https://youtube.com/@lakeviewhall',
                'website_url': 'https://lakeviewhall.example.com',
                'media_uploads': [photo, video],
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)
        venue = Venue.objects.get(id=response.data['id'])
        self.assertEqual(venue.facebook_url, 'https://facebook.com/lakeviewhall')
        self.assertEqual(venue.media.count(), 2)
        self.assertTrue(venue.media.filter(is_video=True).exists())
