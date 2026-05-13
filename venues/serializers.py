from rest_framework import serializers
from .models import Venue, Amenity, VenueMedia, VenueBlock
from vianue.media_utils import uploaded_file_is_video


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('id', 'name')


class VenueMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueMedia
        fields = ('id', 'file', 'is_video', 'description', 'created_at')


class VenueSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone', read_only=True)
    media = VenueMediaSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    media_uploads = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Venue
        fields = (
            'id',
            'owner',
            'owner_name',
            'owner_username',
            'owner_phone',
            'name',
            'venue_type',
            'description',
            'address',
            'city',
            'state',
            'country',
            'pincode',
            'lat',
            'lng',
            'capacity_min',
            'capacity_max',
            'base_price',
            'instagram_url',
            'facebook_url',
            'youtube_url',
            'website_url',
            'rules',
            'cancellation_policy',
            'status',
            'amenities',
            'created_at',
            'updated_at',
            'media',
            'media_uploads',
        )
        read_only_fields = ('owner', 'amenities', 'created_at', 'updated_at', 'media')

    def to_internal_value(self, data):
        if hasattr(data, 'getlist'):
            data = data.copy()
            uploads = data.getlist('media_uploads')
            if uploads:
                data.setlist('media_uploads', uploads)
        return super().to_internal_value(data)

    def create(self, validated_data):
        media_uploads = validated_data.pop('media_uploads', [])
        venue = super().create(validated_data)
        self._save_media(venue, media_uploads)
        return venue

    def update(self, instance, validated_data):
        media_uploads = validated_data.pop('media_uploads', [])
        venue = super().update(instance, validated_data)
        self._save_media(venue, media_uploads)
        return venue

    def _save_media(self, venue, media_uploads):
        for uploaded_file in media_uploads:
            VenueMedia.objects.create(
                venue=venue,
                file=uploaded_file,
                is_video=uploaded_file_is_video(uploaded_file),
            )


class VenueBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueBlock
        fields = '__all__'
