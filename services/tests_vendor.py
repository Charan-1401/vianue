import tempfile

from django.conf import settings
from django.utils import timezone
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User
from orders.models import Order, OrderItem
from payments.models import Payment, Refund
from services.models import ServiceListing, ServiceCategory, ServiceMedia, VendorProfile


class VendorFlowTests(APITestCase):
    def setUp(self):
        self.temp_media_root = tempfile.TemporaryDirectory()
        self.original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.temp_media_root.name
        self.addCleanup(self.cleanup_media_root)

        self.vendor_user = User.objects.create(username='v1', role='VENDOR')
        self.vendor_profile = VendorProfile.objects.get(user=self.vendor_user)
        ServiceCategory.objects.create(name='Photography')
        self.listing = ServiceListing.objects.create(
            vendor=self.vendor_profile,
            title='Photo',
            pricing_model='FIXED',
            base_price=200,
            status='APPROVED',
        )

        self.customer = User.objects.create(username='c1', role='CUSTOMER')
        self.order = Order.objects.create(
            customer=self.customer,
            start_at=timezone.now(),
            end_at=timezone.now() + timezone.timedelta(hours=2),
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            item_type='SERVICE',
            service=self.listing,
            start_at=self.order.start_at,
            end_at=self.order.end_at,
            quantity=1,
            unit_price=220,
            pricing_snapshot={'total': '220'},
        )
        self.client.force_authenticate(user=self.vendor_user)

    def cleanup_media_root(self):
        settings.MEDIA_ROOT = self.original_media_root
        self.temp_media_root.cleanup()

    def test_vendor_accept(self):
        resp = self.client.post(f'/api/services/vendor/requests/{self.item.id}/accept')
        self.assertEqual(resp.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.fulfillment_status, 'ACCEPTED')

    def test_vendor_reject_creates_refund(self):
        payment = Payment.objects.create(order=self.order, amount=220, status='SUCCEEDED')
        resp = self.client.post(f'/api/services/vendor/requests/{self.item.id}/reject', {'reason': "can't do it"})
        self.assertEqual(resp.status_code, 200)
        refund = Refund.objects.filter(payment=payment).first()
        self.assertIsNotNone(refund)

    def test_vendor_can_upload_media_and_social_links(self):
        photo = SimpleUploadedFile('portfolio.jpg', b'photo-bytes', content_type='image/jpeg')
        video = SimpleUploadedFile('promo.mp4', b'video-bytes', content_type='video/mp4')

        response = self.client.post(
            '/api/services/vendor/',
            {
                'title': 'Cinematic team',
                'description': 'Full event coverage',
                'pricing_model': 'FIXED',
                'base_price': '1200.00',
                'min_order_value': '500.00',
                'max_guests_supported': '300',
                'instagram_url': 'https://instagram.com/cinematicteam',
                'facebook_url': 'https://facebook.com/cinematicteam',
                'youtube_url': 'https://youtube.com/@cinematicteam',
                'website_url': 'https://cinematicteam.example.com',
                'media_uploads': [photo, video],
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)
        listing = ServiceListing.objects.get(id=response.data['id'])
        self.assertEqual(listing.instagram_url, 'https://instagram.com/cinematicteam')
        self.assertEqual(listing.media.count(), 2)
        self.assertTrue(ServiceMedia.objects.filter(service=listing, is_video=True).exists())

    def test_service_profile_endpoint_includes_vendor_details(self):
        response = self.client.get(f'/api/services/{self.listing.id}/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.listing.id)
        self.assertIn('vendor', response.data)
        self.assertEqual(response.data['vendor']['business_name'], self.vendor_profile.business_name)

    def test_vendor_profile_read_only_endpoint(self):
        response = self.client.get(f'/api/services/vendor-profiles/{self.vendor_profile.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['business_name'], self.vendor_profile.business_name)
        self.assertEqual(response.data['user'], self.vendor_user.id)
