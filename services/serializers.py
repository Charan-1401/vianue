from rest_framework import serializers
from .models import VendorProfile, ServiceCategory, ServiceListing, ServicePackage, ServiceAddOn


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


class ServiceListingSerializer(serializers.ModelSerializer):
    packages = ServicePackageSerializer(many=True, read_only=True)
    addons = ServiceAddOnSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceListing
        fields = '__all__'
