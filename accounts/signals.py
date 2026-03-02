from django.db.models.signals import post_save
from django.dispatch import receiver

from services.models import VendorProfile

from .models import User


@receiver(post_save, sender=User)
def ensure_vendor_profile(sender, instance, **kwargs):
    if instance.role != "VENDOR":
        return

    VendorProfile.objects.get_or_create(
        user=instance,
        defaults={
            "business_name": instance.get_full_name() or instance.username,
            "phone": instance.phone or "",
        },
    )
