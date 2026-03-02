from rest_framework import serializers
from venues.models import Venue
from services.models import ServiceListing


class SimpleVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ('id', 'name', 'owner', 'city', 'status')


class SimpleServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceListing
        fields = ('id', 'title', 'vendor', 'status')
