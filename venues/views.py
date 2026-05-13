from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsOwnerRole
from .models import Venue, VenueBlock
from .serializers import VenueSerializer, VenueBlockSerializer
from vianue.web_utils import is_available_today


class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Venue.objects.filter(status='APPROVED')
        .select_related('owner')
        .prefetch_related('amenities', 'media', 'blocks')
    )
    serializer_class = VenueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'state', 'address', 'venue_type', 'description', 'pincode']
    ordering_fields = ['base_price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        city = self.request.query_params.get('city', '').strip()
        area = self.request.query_params.get('area', '').strip()
        available = self.request.query_params.get('available_today', '').strip()

        if city:
            qs = qs.filter(
                Q(city__icontains=city)
                | Q(state__icontains=city)
                | Q(address__icontains=city)
            )
        if area:
            qs = qs.filter(
                Q(city__icontains=area)
                | Q(state__icontains=area)
                | Q(address__icontains=area)
                | Q(pincode__icontains=area)
            )

        if available == 'true':
            ids = [
                v.id for v in qs
                if is_available_today(v.blocks.all())
            ]
            qs = qs.filter(id__in=ids)

        return qs

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
        return Response({
            'available': not overlaps.exists(),
            'blocks': VenueBlockSerializer(overlaps, many=True).data,
        })

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        venue = self.get_object()
        serializer = self.get_serializer(venue)
        return Response(serializer.data)


class OwnerVenueViewSet(viewsets.ModelViewSet):
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerRole]

    def get_queryset(self):
        return (
            Venue.objects.filter(owner=self.request.user)
            .select_related('owner')
            .prefetch_related('media')
        )

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

    @action(detail=True, methods=['delete'], url_path='media/(?P<media_id>[^/.]+)')
    def delete_media(self, request, pk=None, media_id=None):
        venue = self.get_object()
        media = get_object_or_404(venue.media.all(), pk=media_id)
        media.file.delete(save=False)
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
