from decimal import Decimal


STAR_VALUES = {
    "love": 5,
    "like": 4,
    "neutral": 3,
    "dislike": 2,
    "hate": 1,
}


def money(value):
    return Decimal(value).quantize(Decimal("0.01"))


def star_summary(perfume):
    scores = [
        STAR_VALUES[sentiment]
        for sentiment in perfume.ratings.values_list("sentiment", flat=True)
        if sentiment in STAR_VALUES
    ]
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 1)


def base_grams(perfume):
    try:
        grams = int(perfume.grams)
    except (TypeError, ValueError):
        grams = 100
    return grams if grams > 0 else 1


def container_amount(perfume, container):
    from apps.perfumes.models import PerfumeContainerPrice

    assigned = PerfumeContainerPrice.objects.filter(perfume=perfume, container=container).first()
    if assigned is not None:
        return Decimal(assigned.price)
    return Decimal(container.price)


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
    total = money(container_amount(perfume, container) + Decimal(extra) * Decimal(perfume.gram_price))
    return grams, total


def build_quote(item):
    from apps.perfumes.models import PerfumeContainerPrice

    perfume = item.perfume
    base = base_grams(perfume)
    assigned = (
        PerfumeContainerPrice.objects.filter(perfume=perfume, container__is_active=True)
        .select_related("container")
        .order_by("price", "container__name")
    )
    options = [
        {
            "id": row.container_id,
            "name": row.container.name,
            "image_url": row.container.image_url,
            "content": row.container.volume or row.container.size,
            "price": format(money(row.price), ".2f"),
            "in_stock": True,
        }
        for row in assigned
    ]
    grams, selected_total = line_total(perfume, item.container, item.grams)
    return {
        "order_id": item.order_id,
        "perfume": {
            "id": perfume.id,
            "name": perfume.name,
            "brand": perfume.brand,
            "image_url": perfume.image_url,
            "price": format(money(perfume.price), ".2f"),
            "stars": star_summary(perfume),
            "chords": list(perfume.main_chords.order_by("name").values_list("name", flat=True)),
        },
        "perfume_option": {
            "name": perfume.name,
            "image_url": perfume.image_url,
            "content": f"{base} g",
            "price": format(money(perfume.price), ".2f"),
            "in_stock": True,
        },
        "base_grams": base,
        "grams": grams,
        "selected_container": item.container_id,
        "unit_price": format(selected_total, ".2f"),
        "total": format(selected_total, ".2f"),
        "containers": options,
    }
