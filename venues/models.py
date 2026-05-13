from django.db import models
from django.conf import settings


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Venue(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='venues')
    name = models.CharField(max_length=255)
    venue_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacity_min = models.PositiveIntegerField(default=1)
    capacity_max = models.PositiveIntegerField(default=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    instagram_url = models.URLField(blank=True, default='')
    facebook_url = models.URLField(blank=True, default='')
    youtube_url = models.URLField(blank=True, default='')
    website_url = models.URLField(blank=True, default='')
    rules = models.JSONField(default=dict, blank=True)
    cancellation_policy = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    amenities = models.ManyToManyField(Amenity, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at'], name='venue_status_created_idx'),
        ]

    def __str__(self):
        return self.name


class VenueMedia(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='venue_media/%Y/%m/%d')
    is_video = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['venue', '-created_at'], name='venuemedia_created_idx'),
        ]

    def __str__(self):
        return f"{self.venue.name} - {self.file.name}"


class VenueBlock(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='blocks')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
