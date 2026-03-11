from django.db import models
from django.conf import settings


class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    cities = models.JSONField(default=list, blank=True)


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)


class ServiceListing(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    )

    PRICING_CHOICES = (
        ('FIXED', 'Fixed'),
        ('PER_HOUR', 'Per Hour'),
        ('PER_GUEST', 'Per Guest'),
        ('CUSTOM_QUOTE', 'Custom Quote'),
    )

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    pricing_model = models.CharField(max_length=20, choices=PRICING_CHOICES, default='FIXED')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_guests_supported = models.PositiveIntegerField(null=True, blank=True)
    instagram_url = models.URLField(blank=True, default='')
    facebook_url = models.URLField(blank=True, default='')
    youtube_url = models.URLField(blank=True, default='')
    website_url = models.URLField(blank=True, default='')
    travel_fee_rule = models.JSONField(default=dict, blank=True)
    cancellation_policy = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServiceMedia(models.Model):
    service = models.ForeignKey(ServiceListing, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='service_media')
    is_video = models.BooleanField(default=False)


class ServicePackage(models.Model):
    listing = models.ForeignKey(ServiceListing, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inclusions = models.JSONField(default=list, blank=True)
    duration_hours = models.PositiveIntegerField(null=True, blank=True)


class ServiceAddOn(models.Model):
    UNIT_CHOICES = (
        ('PER_UNIT', 'Per Unit'),
        ('PER_HOUR', 'Per Hour'),
        ('PER_GUEST', 'Per Guest'),
    )
    listing = models.ForeignKey(ServiceListing, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=20, choices=UNIT_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class VendorBlock(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='blocks')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    reason = models.TextField(blank=True)
