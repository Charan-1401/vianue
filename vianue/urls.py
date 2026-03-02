from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .web_views import (
    AdminDashboardPageView,
    DashboardRedirectView,
    ExplorePageView,
    HomePageView,
    LoginPageView,
    OwnerDashboardPageView,
    RegisterPageView,
    VendorDashboardPageView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('explore/', ExplorePageView.as_view(), name='explore-page'),
    path('login/', LoginPageView.as_view(), name='login-page'),
    path('register/', RegisterPageView.as_view(), name='register-page'),
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard-redirect'),
    path('dashboard/owner/', OwnerDashboardPageView.as_view(), name='owner-dashboard-page'),
    path('dashboard/vendor/', VendorDashboardPageView.as_view(), name='vendor-dashboard-page'),
    path('dashboard/admin/', AdminDashboardPageView.as_view(), name='admin-dashboard-page'),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/', include('accounts.urls')),
    path('api/venues/', include('venues.urls')),
    path('api/services/', include('services.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/availability/', include('availability.urls')),
    path('api/adminpanel/', include('adminpanel.urls')),
]
