from django.db import models


class Payment(models.Model):
    STATUS = (
        ('CREATED', 'Created'),
        ('REQUIRES_ACTION', 'Requires Action'),
        ('SUCCEEDED', 'Succeeded'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    )
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=50, default='stripe')
    provider_payment_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=30, choices=STATUS, default='CREATED')
    raw_payload = models.JSONField(default=dict, blank=True)


class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=30, default='PENDING')
