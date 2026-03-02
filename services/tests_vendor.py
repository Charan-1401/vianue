from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from services.models import VendorProfile, ServiceCategory, ServiceListing
from orders.models import Order, OrderItem
from payments.models import Payment, Refund


class VendorFlowTests(TestCase):
    def setUp(self):
        self.vendor_user = User.objects.create(username='v1', role='VENDOR')
        self.vendor_profile = VendorProfile.objects.create(user=self.vendor_user, business_name='VCo')
        cat = ServiceCategory.objects.create(name='Photography')
        self.listing = ServiceListing.objects.create(vendor=self.vendor_profile, title='Photo', pricing_model='FIXED', base_price=200, status='APPROVED')

        self.customer = User.objects.create(username='c1', role='CUSTOMER')
        self.order = Order.objects.create(customer=self.customer, start_at=timezone.now(), end_at=timezone.now() + timezone.timedelta(hours=2))
        self.item = OrderItem.objects.create(order=self.order, item_type='SERVICE', service=self.listing, start_at=self.order.start_at, end_at=self.order.end_at, quantity=1, unit_price=220, pricing_snapshot={'total':'220'})

    def test_vendor_accept(self):
        self.client.force_login(self.vendor_user)
        resp = self.client.post(f'/api/services/vendor/requests/{self.item.id}/accept')
        self.assertEqual(resp.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.fulfillment_status, 'ACCEPTED')

    def test_vendor_reject_creates_refund(self):
        # create payment
        payment = Payment.objects.create(order=self.order, amount=220, status='SUCCEEDED')
        self.client.force_login(self.vendor_user)
        resp = self.client.post(f'/api/services/vendor/requests/{self.item.id}/reject', {'reason': 'can't do it'})
        self.assertEqual(resp.status_code, 200)
        # refund created
        refund = Refund.objects.filter(payment=payment).first()
        self.assertIsNotNone(refund)
