from rest_framework import serializers
from .models import (
    VendorProfile,
    ServiceCategory,
    ServiceListing,
    ServicePackage,
    ServiceAddOn,
    ServiceMedia,
)
from vianue.media_utils import uploaded_file_is_video


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = '__all__'


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'


class ServicePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePackage
        fields = '__all__'


class ServiceAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAddOn
        fields = '__all__'


class ServiceMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMedia
        fields = ('id', 'file', 'is_video')


class ServiceListingSerializer(serializers.ModelSerializer):
    packages = ServicePackageSerializer(many=True, read_only=True)
    addons = ServiceAddOnSerializer(many=True, read_only=True)
    media = ServiceMediaSerializer(many=True, read_only=True)
    media_uploads = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = ServiceListing
        fields = (
            'id',
            'vendor',
            'title',
            'description',
            'category',
            'pricing_model',
            'base_price',
            'min_order_value',
            'max_guests_supported',
            'instagram_url',
            'facebook_url',
            'youtube_url',
            'website_url',
            'travel_fee_rule',
            'cancellation_policy',
            'status',
            'created_at',
            'updated_at',
            'packages',
            'addons',
            'media',
            'media_uploads',
        )
        read_only_fields = ('vendor', 'created_at', 'updated_at', 'packages', 'addons', 'media')

    def to_internal_value(self, data):
        if hasattr(data, 'getlist'):
            data = data.copy()
            uploads = data.getlist('media_uploads')
            if uploads:
                data.setlist('media_uploads', uploads)
        elif isinstance(data, dict):
            data = data.copy()

        if data.get('max_guests_supported') == '':
            data['max_guests_supported'] = None
        return super().to_internal_value(data)

    def create(self, validated_data):
        media_uploads = validated_data.pop('media_uploads', [])
        listing = super().create(validated_data)
        self._save_media(listing, media_uploads)
        return listing

    def update(self, instance, validated_data):
        media_uploads = validated_data.pop('media_uploads', [])
        listing = super().update(instance, validated_data)
        self._save_media(listing, media_uploads)
        return listing

    def _save_media(self, listing, media_uploads):
        for uploaded_file in media_uploads:
            ServiceMedia.objects.create(
                service=listing,
                file=uploaded_file,
                is_video=uploaded_file_is_video(uploaded_file),
            )
