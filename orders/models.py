from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('REFUNDED', 'Refunded'),
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    event_type = models.CharField(max_length=100, blank=True)
    guest_count = models.PositiveIntegerField(default=0)
    event_city = models.CharField(max_length=100, blank=True)
    event_address = models.CharField(max_length=500, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    totals_snapshot = models.JSONField(default=dict, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    ITEM_TYPES = (('VENUE', 'Venue'), ('SERVICE', 'Service'))
    FULFILLMENT = (
        ('PENDING_ACCEPTANCE', 'Pending Acceptance'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('SCHEDULED', 'Scheduled'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    venue = models.ForeignKey('venues.Venue', on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey('services.ServiceListing', on_delete=models.SET_NULL, null=True, blank=True)
    service_package = models.ForeignKey('services.ServicePackage', on_delete=models.SET_NULL, null=True, blank=True)
    provider_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='provided_items')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pricing_snapshot = models.JSONField(default=dict, blank=True)
    cancellation_policy_snapshot = models.JSONField(default=dict, blank=True)
    fulfillment_status = models.CharField(max_length=30, choices=FULFILLMENT, default='PENDING_ACCEPTANCE')

    class Meta:
        indexes = [
            models.Index(fields=['provider_owner', 'start_at', 'end_at']),
        ]
