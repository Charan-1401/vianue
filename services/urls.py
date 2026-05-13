from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceListingViewSet, VendorListingViewSet, VendorProfileViewSet, PackageViewSet, AddOnViewSet,
    VendorRequestsView, VendorAcceptView, VendorRejectView,
)

router = DefaultRouter()
router.register('vendor-profiles', VendorProfileViewSet, basename='vendor-profiles')
router.register('vendor', VendorListingViewSet, basename='vendor-listings')
router.register('packages', PackageViewSet, basename='packages')
router.register('addons', AddOnViewSet, basename='addons')
router.register('', ServiceListingViewSet, basename='services')

urlpatterns = [
    path('vendor/requests/', VendorRequestsView.as_view(), name='vendor-requests'),
    path('vendor/requests/<int:pk>/accept', VendorAcceptView.as_view(), name='vendor-accept'),
    path('vendor/requests/<int:pk>/reject', VendorRejectView.as_view(), name='vendor-reject'),
    path('', include(router.urls)),
]
