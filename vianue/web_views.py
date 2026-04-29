from collections import Counter
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from rest_framework_simplejwt.authentication import JWTAuthentication

from services.models import ServiceAddOn, ServiceListing, ServicePackage
from venues.models import Venue


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
    return reverse("customer-dashboard-page")


def normalize_keyword(value):
    return "".join(ch for ch in (value or "").lower() if ch.isalnum() or ch.isspace()).strip()


def classify_service_listing(listing):
    fragments = [
        listing.title,
        listing.description,
        getattr(listing.category, "name", ""),
        " ".join(package.name for package in listing.packages.all()),
        " ".join(addon.name for addon in listing.addons.all()),
    ]
    text = normalize_keyword(" ".join(part for part in fragments if part))

    if any(word in text for word in ("photo", "camera", "candid", "cinema", "video")):
        if any(word in text for word in ("cinema", "video", "film", "reel")):
            return "Cinematography"
        return "Photography"
    if any(word in text for word in ("cater", "menu", "buffet", "food", "dining")):
        return "Catering"
    if any(word in text for word in ("decor", "floral", "stage", "styling", "design")):
        return "Decorations"
    if any(word in text for word in ("light", "led", "rig")):
        return "Lighting"
    if any(word in text for word in ("dj", "sound", "music", "audio", "speaker")):
        return "Sound / DJ"
    return getattr(listing.category, "name", "") or "Individual service"


def listing_icon(listing_kind, label):
    normalized = normalize_keyword(label)
    if listing_kind == "venue":
        if "resort" in normalized:
            return "fa-umbrella-beach"
        if "farm" in normalized or "lawn" in normalized or "outdoor" in normalized:
            return "fa-tree"
        if "banquet" in normalized or "hall" in normalized:
            return "fa-champagne-glasses"
        return "fa-hotel"

    if "photo" in normalized:
        return "fa-camera-retro"
    if "cinema" in normalized or "video" in normalized:
        return "fa-video"
    if "cater" in normalized or "food" in normalized:
        return "fa-utensils"
    if "decor" in normalized or "design" in normalized:
        return "fa-wand-magic-sparkles"
    if "light" in normalized:
        return "fa-lightbulb"
    if "sound" in normalized or "dj" in normalized or "music" in normalized:
        return "fa-music"
    return "fa-briefcase"


def format_price(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        return "0"

    quantized = amount.quantize(Decimal("1"))
    if amount == quantized:
        return f"{int(quantized):,}"
    return f"{amount:,.2f}"


def price_unit_for_service(listing):
    if listing.pricing_model == "PER_HOUR":
        return "/hour"
    if listing.pricing_model == "PER_GUEST":
        return "/guest"
    if listing.pricing_model == "CUSTOM_QUOTE":
        return "/quote"
    return "/event"


def venue_matches_location(venue, city, area):
    haystack = " ".join(
        part for part in (venue.name, venue.city, venue.state, venue.address, venue.pincode) if part
    ).lower()
    city_match = city.lower() in haystack if city else True
    area_match = area.lower() in haystack if area else True
    return city_match or area_match


def service_matches_location(listing, city, area):
    cities = [str(item).strip().lower() for item in (listing.vendor.cities or []) if str(item).strip()]
    if not cities:
        return True

    targets = [target.strip().lower() for target in (city, area) if target and target.strip()]
    return any(target in candidate or candidate in target for target in targets for candidate in cities)


def is_available_today(blocks):
    now = timezone.now()
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return not any(block.start_at < end and block.end_at > now for block in blocks)


def base_query_url(city, area, search, category, availability, sort, kind="all"):
    params = {}
    if city:
        params["city"] = city
    if area:
        params["area"] = area
    if search:
        params["q"] = search
    if category:
        params["category"] = category
    if availability:
        params["availability"] = availability
    if sort:
        params["sort"] = sort
    if kind and kind != "all":
        params["kind"] = kind
    query = urlencode(params)
    return f"{reverse('explore-page')}?{query}" if query else reverse("explore-page")


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
        "page_title": "Book Venues and Services",
        "page_key": "home",
    }


class ExplorePageView(TemplateView):
    template_name = "pages/explore.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        city = (request.GET.get("city") or "New York").strip()
        area = (request.GET.get("area") or "").strip()
        search = (request.GET.get("q") or "").strip()
        category = (request.GET.get("category") or "").strip()
        sort = (request.GET.get("sort") or "recommended").strip()
        availability = "today" if request.GET.get("availability") == "today" else ""
        kind = (request.GET.get("kind") or "all").strip()

        normalized_category = normalize_keyword(category)
        if normalized_category == "venues":
            kind = "venues"
        elif normalized_category:
            kind = "services" if kind == "all" else kind

        venues = list(
            Venue.objects.filter(status="APPROVED")
            .prefetch_related("amenities", "media", "blocks")
            .order_by("-created_at")
        )
        services = list(
            ServiceListing.objects.filter(status="APPROVED")
            .select_related("vendor", "category")
            .prefetch_related(
                "vendor__blocks",
                Prefetch("packages", queryset=ServicePackage.objects.order_by("price")),
                Prefetch("addons", queryset=ServiceAddOn.objects.order_by("name")),
            )
            .order_by("-created_at")
        )

        def matches_search(text):
            return not search or search.lower() in text.lower()

        filtered_venues = [
            venue
            for venue in venues
            if matches_search(" ".join(filter(None, [venue.name, venue.venue_type, venue.city, venue.address])))
            and (not normalized_category or normalized_category == "venues" or normalized_category in normalize_keyword(venue.venue_type))
            and (not availability or is_available_today(venue.blocks.all()))
        ]
        filtered_services = [
            listing
            for listing in services
            if matches_search(
                " ".join(
                    filter(
                        None,
                        [
                            listing.title,
                            listing.description,
                            getattr(listing.category, "name", ""),
                            classify_service_listing(listing),
                        ],
                    )
                )
            )
            and (not normalized_category or normalized_category == "venues" or normalized_category in normalize_keyword(classify_service_listing(listing)))
            and (not availability or is_available_today(listing.vendor.blocks.all()))
        ]

        located_venues = [venue for venue in filtered_venues if venue_matches_location(venue, city, area)]
        located_services = [listing for listing in filtered_services if service_matches_location(listing, city, area)]

        location_fallback = False
        if city and not located_venues and not located_services and (filtered_venues or filtered_services):
            located_venues = filtered_venues
            located_services = filtered_services
            location_fallback = True

        venue_cards = [self.build_venue_card(venue) for venue in located_venues]
        service_cards = [self.build_service_card(listing) for listing in located_services]

        if kind == "venues":
            cards = venue_cards
        elif kind == "services":
            cards = service_cards
        else:
            cards = venue_cards + service_cards

        cards.sort(key=lambda item: self.sort_key(item, sort))
        service_counts = Counter(card["summary_label"] for card in service_cards)
        top_venue = Counter(card["type_label"] for card in venue_cards).most_common(1)
        top_service = service_counts.most_common(1)
        suggestion_parts = []
        if top_venue:
            suggestion_parts.append(top_venue[0][0].lower())
        if top_service:
            suggestion_parts.append(top_service[0][0].lower())

        context.update(
            {
                "page_title": "Explore Venues and Services",
                "page_key": "explore",
                "city": city,
                "area": area,
                "search": search,
                "category": category,
                "kind": kind,
                "sort": sort,
                "availability": availability,
                "results": cards,
                "results_count": len(cards),
                "results_label": area or city,
                "location_fallback": location_fallback,
                "filter_tabs": [
                    {
                        "label": "All",
                        "icon": "fa-store",
                        "href": base_query_url(city, area, search, category, availability, sort),
                        "active": kind == "all",
                    },
                    {
                        "label": "Venues",
                        "icon": "fa-building",
                        "href": base_query_url(city, area, search, category, availability, sort, "venues"),
                        "active": kind == "venues",
                    },
                    {
                        "label": "Services",
                        "icon": "fa-camera",
                        "href": base_query_url(city, area, search, category, availability, sort, "services"),
                        "active": kind == "services",
                    },
                    {
                        "label": "Available today",
                        "icon": "fa-calendar-check",
                        "href": base_query_url(
                            city,
                            area,
                            search,
                            category,
                            "today" if not availability else "",
                            sort,
                            kind,
                        ),
                        "active": bool(availability),
                    },
                ],
                "sort_options": [
                    {"value": "recommended", "label": "Recommended"},
                    {"value": "price_low", "label": "Price: low to high"},
                    {"value": "price_high", "label": "Price: high to low"},
                    {"value": "newest", "label": "Newest"},
                ],
                "nearby_services": [
                    {"label": label, "icon": listing_icon("service", label), "count": service_counts.get(label, 0)}
                    for label in (
                        "Photography",
                        "Catering",
                        "Decorations",
                        "Lighting",
                        "Sound / DJ",
                        "Cinematography",
                    )
                    if service_counts.get(label, 0)
                ],
                "suggestion_title": f"{area or city} spotlight",
                "suggestion_body": (
                    f"Strongest mix right now: {' plus '.join(suggestion_parts)}."
                    if suggestion_parts
                    else "Browse approved listings, then tighten the search with location, type, or availability."
                ),
                "location_presets": [
                    {"city": "New York", "area": ""},
                    {"city": "Los Angeles", "area": ""},
                    {"city": "New York", "area": "Manhattan"},
                ],
                "explore_base_url": reverse("explore-page"),
            }
        )
        return context

    def sort_key(self, item, sort):
        if sort == "price_low":
            return (item["price_value"], item["title"].lower())
        if sort == "price_high":
            return (-item["price_value"], item["title"].lower())
        if sort == "newest":
            return (-item["created_order"], item["title"].lower())
        return (-item["score"], item["price_value"], item["title"].lower())

    def build_venue_card(self, venue):
        amenities = [amenity.name for amenity in venue.amenities.all()[:3]]
        location_bits = [bit for bit in [venue.city, venue.state] if bit]
        meta = [
            {
                "icon": "fa-users",
                "text": f"up to {venue.capacity_max} guests",
            },
            {
                "icon": "fa-location-dot",
                "text": ", ".join(location_bits) or venue.address,
            },
        ]
        if amenities:
            tags = amenities
        else:
            tags = [bit for bit in (venue.venue_type, venue.city, "Venue booking") if bit][:3]

        return {
            "kind": "venue",
            "title": venue.name,
            "type_label": ", ".join(location_bits) or venue.address,
            "icon": listing_icon("venue", venue.venue_type or "Venue"),
            "description": venue.description or venue.address,
            "meta": meta,
            "tags": tags,
            "price_display": format_price(venue.base_price),
            "price_unit": "/day",
            "cta_label": "Book now",
            "href": f"/book/?venue_id={venue.id}",
            "price_value": float(venue.base_price or 0),
            "created_order": int(venue.created_at.timestamp()),
            "score": 2 + int(bool(venue.description)) + len(amenities) + int(bool(venue.media.all())),
            "summary_label": "Venue",
        }

    def build_service_card(self, listing):
        summary_label = classify_service_listing(listing)
        packages = [package.name for package in listing.packages.all()[:2]]
        addons = [addon.name for addon in listing.addons.all()[:2]]
        tags = packages + addons
        if not tags:
            tags = [summary_label, "Approved listing"]

        meta = [
            {
                "icon": "fa-bolt",
                "text": summary_label,
            }
        ]
        if listing.max_guests_supported:
            meta.append(
                {
                    "icon": "fa-users",
                    "text": f"supports up to {listing.max_guests_supported} guests",
                }
            )
        else:
            meta.append(
                {
                    "icon": "fa-clock",
                    "text": listing.get_pricing_model_display(),
                }
            )

        return {
            "kind": "service",
            "title": listing.title,
            "type_label": summary_label,
            "icon": listing_icon("service", summary_label),
            "description": listing.description or f"{summary_label} by {listing.vendor.business_name}",
            "meta": meta,
            "tags": tags[:3],
            "price_display": format_price(listing.base_price),
            "price_unit": price_unit_for_service(listing),
            "cta_label": "Book now",
            "href": f"/book/?service_id={listing.id}",
            "price_value": float(listing.base_price or 0),
            "created_order": int(listing.created_at.timestamp()),
            "score": 2 + int(bool(listing.description)) + len(packages) + len(addons),
            "summary_label": summary_label,
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


class CustomerDashboardPageView(ProtectedDashboardView):
    template_name = "pages/customer_dashboard.html"
    extra_context = {
        "page_title": "My Bookings",
        "page_key": "customer-dashboard",
    }


class BookingPageView(ProtectedDashboardView):
    template_name = "pages/booking.html"
    extra_context = {
        "page_title": "Book Venue or Service",
        "page_key": "booking",
    }
