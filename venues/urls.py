from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VenueViewSet, OwnerVenueViewSet

router = DefaultRouter()
router.register('owner', OwnerVenueViewSet, basename='owner-venues')
router.register('', VenueViewSet, basename='venues')

urlpatterns = [
    path('', include(router.urls)),
]
