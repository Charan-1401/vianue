from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, MyOrdersView, VenueOwnerBookingsView, VendorBookingsView, ProviderBookingsView, BookingManagementView

router = DefaultRouter()
router.register('my', MyOrdersView, basename='my-orders')
router.register('', OrderViewSet, basename='orders')
router.register('venue-bookings', VenueOwnerBookingsView, basename='venue-bookings')
router.register('vendor-bookings', VendorBookingsView, basename='vendor-bookings')

urlpatterns = [
    path('', include(router.urls)),
    path('provider-bookings/', ProviderBookingsView.as_view(), name='provider-bookings'),
    path('booking-management/<int:item_id>/', BookingManagementView.as_view(), name='booking-management'),
]
