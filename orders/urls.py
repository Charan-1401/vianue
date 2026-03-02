from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, MyOrdersView

router = DefaultRouter()
router.register('my', MyOrdersView, basename='my-orders')
router.register('', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
