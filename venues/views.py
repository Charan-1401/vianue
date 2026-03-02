from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from accounts.permissions import IsOwnerRole
from .models import Venue, VenueBlock
from .serializers import VenueSerializer, VenueBlockSerializer


class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venue.objects.filter(status='APPROVED')
    serializer_class = VenueSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['city', 'name', 'venue_type']

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        venue = self.get_object()
        start = request.query_params.get('start_at')
        end = request.query_params.get('end_at')
        if not start or not end:
            return Response({'detail': 'start_at and end_at required'}, status=status.HTTP_400_BAD_REQUEST)
        overlaps = VenueBlock.objects.filter(venue=venue).filter(
            Q(start_at__lt=end) & Q(end_at__gt=start)
        )
        return Response({'available': not overlaps.exists(), 'blocks': VenueBlockSerializer(overlaps, many=True).data})


class OwnerVenueViewSet(viewsets.ModelViewSet):
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerRole]

    def get_queryset(self):
        return Venue.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        v = self.get_object()
        v.status = 'PENDING'
        v.save()
        return Response({'status': 'submitted'})
