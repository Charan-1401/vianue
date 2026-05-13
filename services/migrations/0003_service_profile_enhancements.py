# Generated migration for service multimedia and vendor profile enhancements

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_servicemedia_servicelisting_social_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicemedia',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicemedia',
            name='description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='servicemedia',
            name='file',
            field=models.FileField(upload_to='service_media/%Y/%m/%d'),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='portfolio_url',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='instagram_url',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='facebook_url',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='servicelisting',
            index=models.Index(fields=['status', '-created_at'], name='svc_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='servicemedia',
            index=models.Index(fields=['service', '-created_at'], name='svcmedia_created_idx'),
        ),
        migrations.AddIndex(
            model_name='vendorprofile',
            index=models.Index(fields=['is_verified', '-created_at'], name='vendor_verified_idx'),
        ),
    ]
