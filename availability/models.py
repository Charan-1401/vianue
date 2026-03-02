from django.db import models
from django.conf import settings


class Hold(models.Model):
    TARGET_CHOICES = (
        ('VENUE', 'Venue'),
        ('VENDOR', 'Vendor'),
    )
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey('services.VendorProfile', on_delete=models.CASCADE, null=True, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['target_type', 'venue', 'vendor', 'start_at', 'end_at']),
        ]
