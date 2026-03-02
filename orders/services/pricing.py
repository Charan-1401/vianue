from decimal import Decimal

def compute_service_price(listing, package, addons, pricing_model, start_at, end_at, guest_count, quantity):
    hours = max(1, int((end_at - start_at).total_seconds() // 3600))
    subtotal = Decimal('0')
    if package:
        subtotal += Decimal(package.price) * quantity
    else:
        if pricing_model == 'FIXED':
            subtotal += Decimal(listing.base_price) * quantity
        elif pricing_model == 'PER_HOUR':
            subtotal += Decimal(listing.base_price) * Decimal(hours) * quantity
        elif pricing_model == 'PER_GUEST':
            subtotal += Decimal(listing.base_price) * Decimal(guest_count) * quantity
        else:
            raise ValueError('CUSTOM_QUOTE requires manual approval')

    addons_total = Decimal('0')
    for ao in addons:
        unit = ao.unit_type
        price = Decimal(ao.unit_price)
        if unit == 'PER_UNIT':
            addons_total += price * quantity
        elif unit == 'PER_HOUR':
            addons_total += price * Decimal(hours) * quantity
        elif unit == 'PER_GUEST':
            addons_total += price * Decimal(guest_count)
    total = subtotal + addons_total
    tax = (total * Decimal('0.10')).quantize(Decimal('0.01'))
    return {
        'subtotal': str(subtotal),
        'addons': str(addons_total),
        'tax': str(tax),
        'total': str(total + tax),
    }
