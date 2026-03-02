from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from rest_framework_simplejwt.authentication import JWTAuthentication


def get_request_token(request):
    authorization = request.META.get("HTTP_AUTHORIZATION", "")
    if authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1].strip()
    return request.COOKIES.get("vianue_access_token")


def get_jwt_user(request):
    token = get_request_token(request)
    if not token:
        return None

    authenticator = JWTAuthentication()
    try:
        validated_token = authenticator.get_validated_token(token)
        return authenticator.get_user(validated_token)
    except Exception:
        return None


def login_redirect(request):
    params = urlencode({"next": request.get_full_path()})
    return redirect(f"{reverse('login-page')}?{params}")


def resolve_dashboard_path(user):
    if user.is_staff:
        return reverse("admin-dashboard-page")
    if user.role == "OWNER":
        return reverse("owner-dashboard-page")
    if user.role == "VENDOR":
        return reverse("vendor-dashboard-page")
    return reverse("home")


class ProtectedDashboardView(TemplateView):
    allowed_role = None
    require_staff = False

    def dispatch(self, request, *args, **kwargs):
        user = get_jwt_user(request)
        if user is None:
            return login_redirect(request)

        if self.require_staff and not user.is_staff:
            return redirect(resolve_dashboard_path(user))

        if self.allowed_role and user.role != self.allowed_role:
            return redirect(resolve_dashboard_path(user))

        request.dashboard_user = user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dashboard_user"] = getattr(self.request, "dashboard_user", None)
        return context


class HomePageView(TemplateView):
    template_name = "pages/home.html"
    extra_context = {
        "page_title": "Vianue Control Room",
        "page_key": "home",
    }


class LoginPageView(TemplateView):
    template_name = "pages/login.html"
    extra_context = {
        "page_title": "Sign In",
        "page_key": "login",
    }


class RegisterPageView(TemplateView):
    template_name = "pages/register.html"
    extra_context = {
        "page_title": "Create Account",
        "page_key": "register",
    }


class DashboardRedirectView(View):
    def get(self, request, *args, **kwargs):
        user = get_jwt_user(request)
        if user is None:
            return login_redirect(request)
        return redirect(resolve_dashboard_path(user))


class OwnerDashboardPageView(ProtectedDashboardView):
    template_name = "pages/owner_dashboard.html"
    allowed_role = "OWNER"
    extra_context = {
        "page_title": "Owner Dashboard",
        "page_key": "owner-dashboard",
    }


class VendorDashboardPageView(ProtectedDashboardView):
    template_name = "pages/vendor_dashboard.html"
    allowed_role = "VENDOR"
    extra_context = {
        "page_title": "Vendor Dashboard",
        "page_key": "vendor-dashboard",
    }


class AdminDashboardPageView(ProtectedDashboardView):
    template_name = "pages/admin_dashboard.html"
    require_staff = True
    extra_context = {
        "page_title": "Admin Dashboard",
        "page_key": "admin-dashboard",
    }
