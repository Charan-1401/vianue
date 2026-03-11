from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsVendorRole
from orders.models import OrderItem
from payments.models import Payment, Refund

from .models import ServiceAddOn, ServiceListing, ServicePackage, VendorProfile
from .serializers import (
    ServiceAddOnSerializer,
    ServiceListingSerializer,
    ServicePackageSerializer,
)


def get_vendor_profile_for_user(user):
    return VendorProfile.objects.get_or_create(
        user=user,
        defaults={
            "business_name": user.get_full_name() or user.username,
            "phone": user.phone or "",
        },
    )[0]


class ServiceListingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceListing.objects.filter(status='APPROVED').prefetch_related('packages', 'addons', 'media')
    serializer_class = ServiceListingSerializer


class VendorListingViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceListingSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def get_queryset(self):
        return ServiceListing.objects.filter(vendor__user=self.request.user).prefetch_related('media')

    def perform_create(self, serializer):
        serializer.save(vendor=get_vendor_profile_for_user(self.request.user))

    def perform_update(self, serializer):
        serializer.save(vendor=get_vendor_profile_for_user(self.request.user))

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        listing = self.get_object()
        listing.status = 'PENDING'
        listing.save()
        return Response({'status': 'submitted'})

    @action(detail=True, methods=['delete'], url_path='media/(?P<media_id>[^/.]+)')
    def delete_media(self, request, pk=None, media_id=None):
        listing = self.get_object()
        media = get_object_or_404(listing.media.all(), pk=media_id)
        media.file.delete(save=False)
        media.delete()
        return Response(status=204)


class PackageViewSet(viewsets.ModelViewSet):
    serializer_class = ServicePackageSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def get_queryset(self):
        return ServicePackage.objects.filter(listing__vendor__user=self.request.user)

    def perform_create(self, serializer):
        listing = get_object_or_404(
            ServiceListing,
            pk=self.request.data.get("listing"),
            vendor__user=self.request.user,
        )
        serializer.save(listing=listing)

    def perform_update(self, serializer):
        listing_id = self.request.data.get("listing")
        if listing_id:
            listing = get_object_or_404(
                ServiceListing,
                pk=listing_id,
                vendor__user=self.request.user,
            )
            serializer.save(listing=listing)
            return
        serializer.save()


class AddOnViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceAddOnSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def get_queryset(self):
        return ServiceAddOn.objects.filter(listing__vendor__user=self.request.user)

    def perform_create(self, serializer):
        listing = get_object_or_404(
            ServiceListing,
            pk=self.request.data.get("listing"),
            vendor__user=self.request.user,
        )
        serializer.save(listing=listing)

    def perform_update(self, serializer):
        listing_id = self.request.data.get("listing")
        if listing_id:
            listing = get_object_or_404(
                ServiceListing,
                pk=listing_id,
                vendor__user=self.request.user,
            )
            serializer.save(listing=listing)
            return
        serializer.save()


class VendorRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def get(self, request):
        vendor_profile = get_vendor_profile_for_user(request.user)
        items = OrderItem.objects.filter(
            item_type='SERVICE',
            service__vendor=vendor_profile,
            fulfillment_status='PENDING_ACCEPTANCE',
        )
        data = []
        for item in items:
            data.append(
                {
                    'id': item.id,
                    'order_id': item.order.id,
                    'service': item.service.title,
                    'pricing': item.pricing_snapshot,
                }
            )
        return Response(data)


class VendorAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def post(self, request, pk):
        vendor_profile = get_vendor_profile_for_user(request.user)
        item = get_object_or_404(OrderItem, pk=pk, service__vendor=vendor_profile)
        item.fulfillment_status = 'ACCEPTED'
        item.provider_owner = request.user
        item.save()
        return Response({'status': 'accepted'})


class VendorRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def post(self, request, pk):
        reason = request.data.get('reason', '')
        vendor_profile = get_vendor_profile_for_user(request.user)
        item = get_object_or_404(OrderItem, pk=pk, service__vendor=vendor_profile)
        item.fulfillment_status = 'REJECTED'
        item.save()

        succeeded = Payment.objects.filter(order=item.order, status='SUCCEEDED').first()
        if succeeded:
            try:
                amount = Decimal(item.pricing_snapshot.get('total', '0'))
            except Exception:
                amount = Decimal('0')
            Refund.objects.create(payment=succeeded, amount=amount, reason=reason, status='PENDING')

        return Response({'status': 'rejected'})
