from django.urls import path
from .views import (
    AdminPendingVenuesView, AdminApproveVenueView, AdminRejectVenueView,
    AdminPendingServicesView, AdminApproveServiceView, AdminRejectServiceView,
)

urlpatterns = [
    path('venues/pending', AdminPendingVenuesView.as_view()),
    path('venues/<int:pk>/approve', AdminApproveVenueView.as_view()),
    path('venues/<int:pk>/reject', AdminRejectVenueView.as_view()),
    path('services/pending', AdminPendingServicesView.as_view()),
    path('services/<int:pk>/approve', AdminApproveServiceView.as_view()),
    path('services/<int:pk>/reject', AdminRejectServiceView.as_view()),
]
