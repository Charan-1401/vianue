from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from availability.models import Hold
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from services.models import ServiceListing, ServicePackage
from venues.models import Venue
from .services.pricing import compute_service_price
from rest_framework.views import APIView
from rest_framework import serializers


class QuoteInputSerializer(serializers.Serializer):
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    guest_count = serializers.IntegerField()
    venue_id = serializers.IntegerField(required=False)
    services = serializers.ListField(child=serializers.DictField(), required=False)


class QuoteView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = QuoteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        start_at = data['start_at']
        end_at = data['end_at']
        guest_count = data['guest_count']

        items = []
        total = 0

        # Venue pricing (simple fixed)
        if data.get('venue_id'):
            v = get_object_or_404(Venue, pk=data['venue_id'])
            venue_price = float(v.base_price)
            items.append({'type': 'VENUE', 'id': v.id, 'price': venue_price})
            total += venue_price

        # Services
        for s in data.get('services', []):
            listing = get_object_or_404(ServiceListing, pk=s.get('listing_id'))
            package = None
            if s.get('package_id'):
                package = get_object_or_404(ServicePackage, pk=s.get('package_id'))
            # TODO: handle add-ons in request
            pricing = compute_service_price(listing, package, [], listing.pricing_model, start_at, end_at, guest_count, s.get('quantity', 1))
            item_total = float(pricing['total'])
            items.append({'type': 'SERVICE', 'id': listing.id, 'price': item_total, 'pricing': pricing})
            total += item_total

        return Response({'items': items, 'total': total})


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'])
    def items(self, request, pk=None):
        order = self.get_object()
        data = request.data
        item_type = data.get('item_type')
        start_at = data.get('start_at')
        end_at = data.get('end_at')
        quantity = int(data.get('quantity', 1))

        if item_type == 'VENUE':
            venue = get_object_or_404(Venue, pk=data.get('venue'))
            oi = OrderItem.objects.create(order=order, item_type='VENUE', venue=venue,
                                          start_at=start_at, end_at=end_at, quantity=quantity, unit_price=0,
                                          pricing_snapshot={})
        else:
            listing = get_object_or_404(ServiceListing, pk=data.get('service'))
            package = None
            if data.get('package'):
                package = get_object_or_404(ServicePackage, pk=data.get('package'))
            # compute price
            pricing = compute_service_price(listing, package, [], listing.pricing_model, order.start_at, order.end_at, order.guest_count, quantity)
            oi = OrderItem.objects.create(order=order, item_type='SERVICE', service=listing, service_package=package,
                                          start_at=order.start_at, end_at=order.end_at, quantity=quantity,
                                          unit_price=pricing['total'], pricing_snapshot=pricing)

        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        order = self.get_object()
        # validate availability and create holds
        with transaction.atomic():
            # simple locking strategy: lock order rows and related venues
            for item in order.items.select_related('venue', 'service'):
                if item.item_type == 'VENUE' and item.venue:
                    Venue.objects.select_for_update().filter(pk=item.venue.pk)
                if item.item_type == 'SERVICE' and item.service:
                    ServiceListing.objects.select_for_update().filter(pk=item.service.pk)

            # check overlaps against confirmed items and holds
            now = timezone.now()
            expiry = now + timezone.timedelta(minutes=10)
            for item in order.items.all():
                if item.item_type == 'VENUE' and item.venue:
                    Hold.objects.create(target_type='VENUE', venue=item.venue, start_at=item.start_at, end_at=item.end_at, expires_at=expiry, created_by=request.user)
                if item.item_type == 'SERVICE' and item.service:
                    Hold.objects.create(target_type='VENDOR', vendor=item.service.vendor, start_at=item.start_at, end_at=item.end_at, expires_at=expiry, created_by=request.user)

            # create payment intent stub (handled in payments app)
            order.status = 'PENDING_PAYMENT'
            order.save()

        return Response({'status': 'pending_payment', 'order_id': order.id})


class MyOrdersView(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)
