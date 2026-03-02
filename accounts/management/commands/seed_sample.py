from django.core.management.base import BaseCommand

from accounts.models import User
from venues.models import Venue, Amenity
from services.models import VendorProfile, ServiceCategory, ServiceListing


class Command(BaseCommand):
    help = 'Seed sample users, venues, services'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'role': 'ADMIN', 'is_staff': True})
        admin.set_password('admin')
        admin.save()

        owner, _ = User.objects.get_or_create(username='owner', defaults={'email': 'owner@example.com', 'role': 'OWNER'})
        owner.set_password('owner')
        owner.save()

        vendor_user, _ = User.objects.get_or_create(username='vendor', defaults={'email': 'vendor@example.com', 'role': 'VENDOR'})
        vendor_user.set_password('vendor')
        vendor_user.save()

        customer, _ = User.objects.get_or_create(username='customer', defaults={'email': 'customer@example.com', 'role': 'CUSTOMER'})
        customer.set_password('customer')
        customer.save()

        wifi, _ = Amenity.objects.get_or_create(name='WiFi')
        parking, _ = Amenity.objects.get_or_create(name='Parking')

        v, _ = Venue.objects.get_or_create(owner=owner, name='Sample Hall', city='Metropolis', address='123 Main St', capacity_min=10, capacity_max=300)
        v.amenities.add(wifi, parking)

        vp, _ = VendorProfile.objects.get_or_create(user=vendor_user, business_name='VendorCo')
        cat, _ = ServiceCategory.objects.get_or_create(name='Catering')
        sl, _ = ServiceListing.objects.get_or_create(vendor=vp, title='Standard Catering', category=cat, base_price=1000, pricing_model='FIXED', status='APPROVED')

        self.stdout.write(self.style.SUCCESS('Seeded sample data'))
