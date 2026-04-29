from decimal import Decimal
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from venues.models import Venue, Amenity, VenueMedia, VenueBlock
from services.models import (
    VendorProfile, ServiceCategory, ServiceListing,
    ServiceMedia, ServicePackage, ServiceAddOn, VendorBlock
)
from availability.models import Hold
from orders.models import Order, OrderItem
from payments.models import Payment, Refund


class Command(BaseCommand):
    help = 'Seed complete sample data for all models'

    def handle(self, *args, **options):
        # Use a fixed reference date for idempotency
        ref = datetime(2026, 6, 1, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # --- Users ---
        self.stdout.write('Seeding Users...')
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@vianue.com',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'phone': '+10000000000',
            }
        )
        admin.set_password('admin123')
        admin.save()

        owner1, _ = User.objects.get_or_create(
            username='owner1',
            defaults={
                'email': 'owner1@vianue.com',
                'role': 'OWNER',
                'phone': '+10000000001',
            }
        )
        owner1.set_password('owner123')
        owner1.save()

        owner2, _ = User.objects.get_or_create(
            username='owner2',
            defaults={
                'email': 'owner2@vianue.com',
                'role': 'OWNER',
                'phone': '+10000000002',
            }
        )
        owner2.set_password('owner123')
        owner2.save()

        vendor1_user, _ = User.objects.get_or_create(
            username='vendor1',
            defaults={
                'email': 'vendor1@vianue.com',
                'role': 'VENDOR',
                'phone': '+10000000003',
            }
        )
        vendor1_user.set_password('vendor123')
        vendor1_user.save()

        vendor2_user, _ = User.objects.get_or_create(
            username='vendor2',
            defaults={
                'email': 'vendor2@vianue.com',
                'role': 'VENDOR',
                'phone': '+10000000004',
            }
        )
        vendor2_user.set_password('vendor123')
        vendor2_user.save()

        customer1, _ = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer1@vianue.com',
                'role': 'CUSTOMER',
                'phone': '+10000000005',
            }
        )
        customer1.set_password('customer123')
        customer1.save()

        customer2, _ = User.objects.get_or_create(
            username='customer2',
            defaults={
                'email': 'customer2@vianue.com',
                'role': 'CUSTOMER',
                'phone': '+10000000006',
            }
        )
        customer2.set_password('customer123')
        customer2.save()

        self.stdout.write(self.style.SUCCESS(f'  Created users: {admin.username}, {owner1.username}, {owner2.username}, {vendor1_user.username}, {vendor2_user.username}, {customer1.username}, {customer2.username}'))

        # --- Amenities ---
        self.stdout.write('Seeding Amenities...')
        amenities_data = ['WiFi', 'Parking', 'Pool', 'Catering Kitchen', 'Stage', 'Projector', 'Sound System', 'Garden', 'Bar', 'Dance Floor']
        amenities = []
        for name in amenities_data:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            amenities.append(amenity)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(amenities)} amenities'))

        # --- Venues ---
        self.stdout.write('Seeding Venues...')
        venue1, _ = Venue.objects.get_or_create(
            owner=owner1,
            name='Grand Ballroom',
            defaults={
                'venue_type': 'Ballroom',
                'description': 'Elegant ballroom for large events and weddings.',
                'address': '100 Celebration Ave',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'pincode': '10001',
                'lat': Decimal('40.7128'),
                'lng': Decimal('-74.0060'),
                'capacity_min': 50,
                'capacity_max': 500,
                'base_price': Decimal('5000.00'),
                'status': 'APPROVED',
                'rules': {'no_smoking': True, 'pets_allowed': False},
                'cancellation_policy': {'full_refund_days': 30, 'partial_refund_days': 14},
            }
        )
        venue1.amenities.set(amenities[:5])

        venue2, _ = Venue.objects.get_or_create(
            owner=owner1,
            name='Rooftop Terrace',
            defaults={
                'venue_type': 'Rooftop',
                'description': 'Open-air rooftop venue with city views.',
                'address': '200 Skyline Blvd, Floor 20',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'pincode': '10002',
                'lat': Decimal('40.7200'),
                'lng': Decimal('-73.9900'),
                'capacity_min': 20,
                'capacity_max': 150,
                'base_price': Decimal('3000.00'),
                'status': 'APPROVED',
                'rules': {'no_smoking': False, 'pets_allowed': True},
                'cancellation_policy': {'full_refund_days': 21, 'partial_refund_days': 7},
            }
        )
        venue2.amenities.set(amenities[3:8])

        venue3, _ = Venue.objects.get_or_create(
            owner=owner2,
            name='Garden Pavilion',
            defaults={
                'venue_type': 'Garden',
                'description': 'Beautiful outdoor garden pavilion.',
                'address': '300 Greenway Dr',
                'city': 'Los Angeles',
                'state': 'CA',
                'country': 'USA',
                'pincode': '90001',
                'lat': Decimal('34.0522'),
                'lng': Decimal('-118.2437'),
                'capacity_min': 30,
                'capacity_max': 200,
                'base_price': Decimal('2500.00'),
                'status': 'APPROVED',
                'rules': {'no_smoking': True, 'pets_allowed': True},
                'cancellation_policy': {'full_refund_days': 45, 'partial_refund_days': 20},
            }
        )
        venue3.amenities.set(amenities[5:])

        self.stdout.write(self.style.SUCCESS(f'  Created venues: {venue1.name}, {venue2.name}, {venue3.name}'))

        # --- Vendor Profiles ---
        self.stdout.write('Seeding Vendor Profiles...')
        vendor1, _ = VendorProfile.objects.update_or_create(
            user=vendor1_user,
            defaults={
                'business_name': 'Gourmet Delights Catering',
                'phone': '+10000000003',
                'is_verified': True,
                'cities': ['New York', 'Los Angeles'],
            }
        )

        vendor2, _ = VendorProfile.objects.update_or_create(
            user=vendor2_user,
            defaults={
                'business_name': 'SnapShot Photography',
                'phone': '+10000000004',
                'is_verified': True,
                'cities': ['New York'],
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  Created vendors: {vendor1.business_name}, {vendor2.business_name}'))

        # --- Service Categories ---
        self.stdout.write('Seeding Service Categories...')
        categories_data = ['Catering', 'Photography', 'Music & DJ', 'Florals', 'Decor']
        categories = []
        for name in categories_data:
            cat, _ = ServiceCategory.objects.get_or_create(name=name)
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(categories)} categories'))

        # --- Service Listings ---
        self.stdout.write('Seeding Service Listings...')
        service1, _ = ServiceListing.objects.get_or_create(
            vendor=vendor1,
            title='Premium Wedding Catering Package',
            defaults={
                'description': 'Full-service catering with custom menus for weddings and large events.',
                'category': categories[0],
                'pricing_model': 'PER_GUEST',
                'base_price': Decimal('85.00'),
                'min_order_value': Decimal('1000.00'),
                'max_guests_supported': 500,
                'instagram_url': 'https://instagram.com/gourmetdelights',
                'facebook_url': '',
                'youtube_url': '',
                'website_url': 'https://gourmetdelights.example.com',
                'travel_fee_rule': {'base_fee': 100, 'per_mile': 2.5},
                'cancellation_policy': {'full_refund_days': 30, 'partial_refund_days': 14},
                'status': 'APPROVED',
            }
        )

        service2, _ = ServiceListing.objects.get_or_create(
            vendor=vendor2,
            title='Professional Event Photography',
            defaults={
                'description': 'Professional photography coverage for events, includes edited digital gallery.',
                'category': categories[1],
                'pricing_model': 'PER_HOUR',
                'base_price': Decimal('250.00'),
                'min_order_value': Decimal('500.00'),
                'max_guests_supported': None,
                'instagram_url': 'https://instagram.com/snapshot',
                'facebook_url': '',
                'youtube_url': '',
                'website_url': 'https://snapshot.example.com',
                'travel_fee_rule': {'base_fee': 50, 'per_mile': 1.0},
                'cancellation_policy': {'full_refund_days': 21, 'partial_refund_days': 7},
                'status': 'APPROVED',
            }
        )

        service3, _ = ServiceListing.objects.get_or_create(
            vendor=vendor1,
            title='Corporate Lunch Buffet',
            defaults={
                'description': 'Buffet-style catering for corporate events.',
                'category': categories[0],
                'pricing_model': 'FIXED',
                'base_price': Decimal('750.00'),
                'min_order_value': Decimal('500.00'),
                'max_guests_supported': 100,
                'instagram_url': '',
                'facebook_url': '',
                'youtube_url': '',
                'website_url': '',
                'travel_fee_rule': {},
                'cancellation_policy': {},
                'status': 'APPROVED',
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  Created services: {service1.title}, {service2.title}, {service3.title}'))

        # --- Service Packages ---
        self.stdout.write('Seeding Service Packages...')
        package1, _ = ServicePackage.objects.get_or_create(
            listing=service1,
            name='Silver Package',
            defaults={
                'price': Decimal('65.00'),
                'inclusions': ['Appetizers', 'Main Course', 'Dessert', 'Non-alcoholic Beverages'],
                'duration_hours': 4,
            }
        )

        package2, _ = ServicePackage.objects.get_or_create(
            listing=service1,
            name='Gold Package',
            defaults={
                'price': Decimal('95.00'),
                'inclusions': ['Appetizers', 'Main Course', 'Dessert', 'Full Bar', 'Wedding Cake'],
                'duration_hours': 6,
            }
        )

        package3, _ = ServicePackage.objects.get_or_create(
            listing=service2,
            name='Half-Day Coverage',
            defaults={
                'price': Decimal('1000.00'),
                'inclusions': ['4 hours coverage', 'Online gallery', '50 edited photos'],
                'duration_hours': 4,
            }
        )

        package4, _ = ServicePackage.objects.get_or_create(
            listing=service2,
            name='Full-Day Coverage',
            defaults={
                'price': Decimal('2000.00'),
                'inclusions': ['8 hours coverage', 'Online gallery', '200 edited photos', 'Second photographer'],
                'duration_hours': 8,
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {ServicePackage.objects.count()} packages'))

        # --- Service Add-Ons ---
        self.stdout.write('Seeding Service Add-Ons...')
        addon1, _ = ServiceAddOn.objects.get_or_create(
            listing=service1,
            name='Premium Wine Pairing',
            defaults={
                'unit_type': 'PER_GUEST',
                'unit_price': Decimal('25.00'),
            }
        )

        addon2, _ = ServiceAddOn.objects.get_or_create(
            listing=service1,
            name='Late Night Snack Station',
            defaults={
                'unit_type': 'PER_UNIT',
                'unit_price': Decimal('350.00'),
            }
        )

        addon3, _ = ServiceAddOn.objects.get_or_create(
            listing=service2,
            name='Photo Booth',
            defaults={
                'unit_type': 'PER_HOUR',
                'unit_price': Decimal('200.00'),
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {ServiceAddOn.objects.count()} add-ons'))

        # --- Venue Blocks ---
        self.stdout.write('Seeding Venue Blocks...')
        VenueBlock.objects.filter(venue=venue1, start_at=ref + timedelta(days=10)).delete()
        VenueBlock.objects.create(
            venue=venue1,
            start_at=ref + timedelta(days=10),
            end_at=ref + timedelta(days=10, hours=8),
            reason='Private event',
            created_by=admin,
        )

        VenueBlock.objects.filter(venue=venue2, start_at=ref + timedelta(days=15)).delete()
        VenueBlock.objects.create(
            venue=venue2,
            start_at=ref + timedelta(days=15),
            end_at=ref + timedelta(days=15, hours=6),
            reason='Maintenance',
            created_by=owner1,
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {VenueBlock.objects.count()} venue blocks'))

        # --- Vendor Blocks ---
        self.stdout.write('Seeding Vendor Blocks...')
        VendorBlock.objects.filter(vendor=vendor1, start_at=ref + timedelta(days=20)).delete()
        VendorBlock.objects.create(
            vendor=vendor1,
            start_at=ref + timedelta(days=20),
            end_at=ref + timedelta(days=22),
            reason='Unavailable - scheduled maintenance',
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {VendorBlock.objects.count()} vendor blocks'))

        # --- Holds ---
        self.stdout.write('Seeding Holds...')
        Hold.objects.filter(target_type='VENUE', venue=venue1, start_at=ref + timedelta(days=30)).delete()
        Hold.objects.create(
            target_type='VENUE',
            venue=venue1,
            vendor=None,
            start_at=ref + timedelta(days=30),
            end_at=ref + timedelta(days=30, hours=6),
            expires_at=ref + timedelta(days=8),
            created_by=customer1,
        )

        Hold.objects.filter(target_type='VENDOR', vendor=vendor2, start_at=ref + timedelta(days=35)).delete()
        Hold.objects.create(
            target_type='VENDOR',
            venue=None,
            vendor=vendor2,
            start_at=ref + timedelta(days=35),
            end_at=ref + timedelta(days=35, hours=4),
            expires_at=ref + timedelta(days=10),
            created_by=customer1,
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {Hold.objects.count()} holds'))

        # --- Orders ---
        self.stdout.write('Seeding Orders...')
        order1, _ = Order.objects.get_or_create(
            customer=customer1,
            event_type='Wedding',
            event_city='New York',
            defaults={
                'guest_count': 200,
                'event_address': '100 Celebration Ave',
                'start_at': ref + timedelta(days=30),
                'end_at': ref + timedelta(days=30, hours=10),
                'status': 'CONFIRMED',
                'totals_snapshot': {
                    'venue': '5000.00',
                    'services': '3200.00',
                    'addons': '5000.00',
                    'total': '13200.00',
                },
                'currency': 'USD',
            }
        )

        order2, _ = Order.objects.get_or_create(
            customer=customer2,
            event_type='Corporate Event',
            event_city='Los Angeles',
            defaults={
                'guest_count': 80,
                'event_address': '300 Greenway Dr',
                'start_at': ref + timedelta(days=45),
                'end_at': ref + timedelta(days=45, hours=6),
                'status': 'PENDING_PAYMENT',
                'totals_snapshot': {
                    'venue': '2500.00',
                    'services': '750.00',
                    'addons': '0.00',
                    'total': '3250.00',
                },
                'currency': 'USD',
            }
        )

        order3, _ = Order.objects.get_or_create(
            customer=customer1,
            event_type='Birthday Party',
            event_city='New York',
            defaults={
                'guest_count': 50,
                'event_address': '200 Skyline Blvd',
                'start_at': ref + timedelta(days=60),
                'end_at': ref + timedelta(days=60, hours=5),
                'status': 'COMPLETED',
                'totals_snapshot': {
                    'venue': '3000.00',
                    'services': '1000.00',
                    'addons': '0.00',
                    'total': '4000.00',
                },
                'currency': 'USD',
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {Order.objects.count()} orders'))

        # --- Order Items ---
        self.stdout.write('Seeding Order Items...')
        OrderItem.objects.filter(order=order1).delete()
        OrderItem.objects.create(
            order=order1,
            item_type='VENUE',
            venue=venue1,
            service=None,
            service_package=None,
            provider_owner=owner1,
            start_at=ref + timedelta(days=30),
            end_at=ref + timedelta(days=30, hours=10),
            quantity=1,
            unit_price=Decimal('5000.00'),
            pricing_snapshot={'base_price': '5000.00'},
            cancellation_policy_snapshot=venue1.cancellation_policy,
            fulfillment_status='ACCEPTED',
        )

        OrderItem.objects.create(
            order=order1,
            item_type='SERVICE',
            venue=None,
            service=service1,
            service_package=package2,
            provider_owner=vendor1_user,
            start_at=ref + timedelta(days=30),
            end_at=ref + timedelta(days=30, hours=10),
            quantity=200,
            unit_price=Decimal('95.00'),
            pricing_snapshot={'package_price': '95.00', 'pricing_model': 'PER_GUEST'},
            cancellation_policy_snapshot=service1.cancellation_policy,
            fulfillment_status='ACCEPTED',
        )

        OrderItem.objects.create(
            order=order1,
            item_type='SERVICE',
            venue=None,
            service=service2,
            service_package=package4,
            provider_owner=vendor2_user,
            start_at=ref + timedelta(days=30),
            end_at=ref + timedelta(days=30, hours=10),
            quantity=1,
            unit_price=Decimal('2000.00'),
            pricing_snapshot={'package_price': '2000.00', 'pricing_model': 'FIXED'},
            cancellation_policy_snapshot=service2.cancellation_policy,
            fulfillment_status='ACCEPTED',
        )

        OrderItem.objects.filter(order=order2).delete()
        OrderItem.objects.create(
            order=order2,
            item_type='VENUE',
            venue=venue3,
            service=None,
            service_package=None,
            provider_owner=owner2,
            start_at=ref + timedelta(days=45),
            end_at=ref + timedelta(days=45, hours=6),
            quantity=1,
            unit_price=Decimal('2500.00'),
            pricing_snapshot={'base_price': '2500.00'},
            cancellation_policy_snapshot=venue3.cancellation_policy,
            fulfillment_status='PENDING_ACCEPTANCE',
        )

        OrderItem.objects.create(
            order=order2,
            item_type='SERVICE',
            venue=None,
            service=service3,
            service_package=None,
            provider_owner=vendor1_user,
            start_at=ref + timedelta(days=45),
            end_at=ref + timedelta(days=45, hours=6),
            quantity=1,
            unit_price=Decimal('750.00'),
            pricing_snapshot={'base_price': '750.00', 'pricing_model': 'FIXED'},
            cancellation_policy_snapshot=service3.cancellation_policy,
            fulfillment_status='PENDING_ACCEPTANCE',
        )

        OrderItem.objects.filter(order=order3).delete()
        OrderItem.objects.create(
            order=order3,
            item_type='VENUE',
            venue=venue2,
            service=None,
            service_package=None,
            provider_owner=owner1,
            start_at=ref + timedelta(days=-30),
            end_at=ref + timedelta(days=-30, hours=5),
            quantity=1,
            unit_price=Decimal('3000.00'),
            pricing_snapshot={'base_price': '3000.00'},
            cancellation_policy_snapshot=venue2.cancellation_policy,
            fulfillment_status='DELIVERED',
        )

        OrderItem.objects.create(
            order=order3,
            item_type='SERVICE',
            venue=None,
            service=service2,
            service_package=package3,
            provider_owner=vendor2_user,
            start_at=ref + timedelta(days=-30),
            end_at=ref + timedelta(days=-30, hours=5),
            quantity=1,
            unit_price=Decimal('1000.00'),
            pricing_snapshot={'package_price': '1000.00', 'pricing_model': 'FIXED'},
            cancellation_policy_snapshot=service2.cancellation_policy,
            fulfillment_status='DELIVERED',
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {OrderItem.objects.count()} order items'))

        # --- Payments ---
        self.stdout.write('Seeding Payments...')
        Payment.objects.filter(order=order1).delete()
        payment1 = Payment.objects.create(
            order=order1,
            provider='stripe',
            provider_payment_id='pi_sample123456',
            amount=Decimal('13200.00'),
            currency='USD',
            status='SUCCEEDED',
            raw_payload={'charge_id': 'ch_sample123', 'receipt_url': 'https://stripe.example.com/receipt/123'},
        )

        Payment.objects.filter(order=order2).delete()
        payment2 = Payment.objects.create(
            order=order2,
            provider='stripe',
            provider_payment_id='pi_sample789012',
            amount=Decimal('3250.00'),
            currency='USD',
            status='REQUIRES_ACTION',
            raw_payload={'requires_action': True},
        )

        payment3, _ = Payment.objects.get_or_create(
            order=order3,
            provider='stripe',
            provider_payment_id='pi_sample345678',
            amount=Decimal('4000.00'),
            currency='USD',
            status='SUCCEEDED',
            raw_payload={'charge_id': 'ch_sample345', 'receipt_url': 'https://stripe.example.com/receipt/345'},
        )

        # --- Refunds ---
        self.stdout.write('Seeding Refunds...')
        Refund.objects.filter(payment=payment3).delete()
        Refund.objects.create(
            payment=payment3,
            amount=Decimal('500.00'),
            reason='Partial refund for unused services',
            status='SUCCEEDED',
        )

        payment2, _ = Payment.objects.get_or_create(
            order=order2,
            provider='stripe',
            provider_payment_id='pi_sample789012',
            amount=Decimal('3250.00'),
            currency='USD',
            status='REQUIRES_ACTION',
            raw_payload={'requires_action': True},
        )

        payment3, _ = Payment.objects.get_or_create(
            order=order3,
            provider='stripe',
            provider_payment_id='pi_sample345678',
            amount=Decimal('4000.00'),
            currency='USD',
            status='SUCCEEDED',
            raw_payload={'charge_id': 'ch_sample345', 'receipt_url': 'https://stripe.example.com/receipt/345'},
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {Payment.objects.count()} payments'))

        # --- Refunds ---
        self.stdout.write('Seeding Refunds...')
        Refund.objects.get_or_create(
            payment=payment3,
            amount=Decimal('500.00'),
            reason='Partial refund for unused services',
            status='SUCCEEDED',
        )

        self.stdout.write(self.style.SUCCESS(f'  Created {Refund.objects.count()} refunds'))

        # --- Summary ---
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Seed Data Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'  Users:                {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Amenities:            {Amenity.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Venues:               {Venue.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Vendor Profiles:      {VendorProfile.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Service Categories:   {ServiceCategory.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Service Listings:     {ServiceListing.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Service Packages:     {ServicePackage.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Service Add-Ons:      {ServiceAddOn.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Venue Blocks:         {VenueBlock.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Vendor Blocks:        {VendorBlock.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Holds:                {Hold.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Orders:               {Order.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Order Items:          {OrderItem.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Payments:             {Payment.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Refunds:              {Refund.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('========================='))
        self.stdout.write(self.style.SUCCESS('All seed data created successfully!'))
