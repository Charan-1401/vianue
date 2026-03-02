from rest_framework import serializers
from .models import Venue, Amenity, VenueMedia, VenueBlock


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('id', 'name')


class VenueMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueMedia
        fields = ('id', 'file', 'is_video')


class VenueSerializer(serializers.ModelSerializer):
    media = VenueMediaSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)

    class Meta:
        model = Venue
        fields = '__all__'


class VenueBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueBlock
        fields = '__all__'
