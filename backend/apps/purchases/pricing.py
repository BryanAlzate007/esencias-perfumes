from decimal import Decimal


def money(value):
    return Decimal(value).quantize(Decimal("0.01"))


def base_grams(perfume):
    try:
        grams = int(perfume.grams)
    except (TypeError, ValueError):
        grams = 100
    return grams if grams > 0 else 1


def line_total(perfume, container, grams):
    base = base_grams(perfume)
    if container is None:
        return base, money(perfume.price)
    try:
        requested = int(grams)
    except (TypeError, ValueError):
        requested = base
    grams = max(requested, base)
    extra = grams - base
    total = money(Decimal(container.price) + Decimal(extra) * Decimal(perfume.gram_price))
    return grams, total


def build_quote(item):
    from apps.perfumes.models import Container

    perfume = item.perfume
    base = base_grams(perfume)
    options = [
        {
            "id": container.id,
            "name": container.name,
            "image_url": container.image_url,
        }
        for container in Container.objects.filter(is_active=True).order_by("name")
    ]
    grams, selected_total = line_total(perfume, item.container, item.grams)
    return {
        "order_id": item.order_id,
        "perfume": {
            "id": perfume.id,
            "name": perfume.name,
            "image_url": perfume.image_url,
            "price": format(money(perfume.price), ".2f"),
        },
        "base_grams": base,
        "grams": grams,
        "selected_container": item.container_id,
        "unit_price": format(selected_total, ".2f"),
        "total": format(selected_total, ".2f"),
        "containers": options,
    }
