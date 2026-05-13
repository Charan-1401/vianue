# Generated migration for multimedia and public profile enhancements

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0002_venue_social_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='venuemedia',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venuemedia',
            name='description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='venuemedia',
            name='file',
            field=models.FileField(upload_to='venue_media/%Y/%m/%d'),
        ),
        migrations.AddIndex(
            model_name='venue',
            index=models.Index(fields=['status', '-created_at'], name='venue_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='venuemedia',
            index=models.Index(fields=['venue', '-created_at'], name='venuemedia_created_idx'),
        ),
    ]
