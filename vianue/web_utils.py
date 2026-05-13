from decimal import Decimal, InvalidOperation
from django.utils import timezone


def is_available_today(blocks):
    now = timezone.now()
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return not any(block.start_at < end and block.end_at > now for block in blocks)


def format_price(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        return "0"
    quantized = amount.quantize(Decimal("1"))
    if amount == quantized:
        return f"{int(quantized):,}"
    return f"{amount:,.2f}"


def classify_service_listing(listing):
    text_parts = [
        listing.title,
        listing.description or "",
        getattr(listing.category, "name", ""),
        " ".join(p.name for p in listing.packages.all()),
        " ".join(a.name for a in listing.addons.all()),
    ]
    text = " ".join(p.lower() for p in text_parts if p)

    if any(w in text for w in ("photo", "camera", "candid")):
        if any(w in text for w in ("cinema", "video", "film", "reel")):
            return "Cinematography"
        return "Photography"
    if any(w in text for w in ("cater", "menu", "buffet", "food", "dining")):
        return "Catering"
    if any(w in text for w in ("decor", "floral", "stage", "styling", "design")):
        return "Decorations"
    if any(w in text for w in ("light", "led", "rig")):
        return "Lighting"
    if any(w in text for w in ("dj", "sound", "music", "audio", "speaker")):
        return "Sound / DJ"
    return getattr(listing.category, "name", "") or "Individual service"


def listing_icon(kind, label):
    norm = (label or "").lower()
    if kind == "venue":
        if "resort" in norm:
            return "fa-umbrella-beach"
        if "farm" in norm or "lawn" in norm or "outdoor" in norm:
            return "fa-tree"
        if "banquet" in norm or "hall" in norm:
            return "fa-champagne-glasses"
        return "fa-hotel"
    if "photo" in norm:
        return "fa-camera-retro"
    if "cinema" in norm or "video" in norm:
        return "fa-video"
    if "cater" in norm or "food" in norm:
        return "fa-utensils"
    if "decor" in norm:
        return "fa-wand-magic-sparkles"
    if "light" in norm:
        return "fa-lightbulb"
    if "sound" in norm or "dj" in norm or "music" in norm:
        return "fa-music"
    return "fa-briefcase"


def price_unit_for_service(listing):
    model = listing.pricing_model
    if model == "PER_HOUR":
        return "/hour"
    if model == "PER_GUEST":
        return "/guest"
    if model == "CUSTOM_QUOTE":
        return "/quote"
    return "/event"
