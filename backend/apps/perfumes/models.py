from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


def media_path(image_field):
    if not image_field:
        return ""
    url = image_field.url
    if url.startswith(("http://", "https://", "/")):
        return url
    return f"/{url}"


def related_image_url(images):
    stored = list(images.all())
    image = next((item for item in stored if item.is_primary), None)
    if image is None and stored:
        image = stored[0]
    if image is None:
        return ""
    return media_path(image.image)


class Perfume(models.Model):
    class Catalog(models.TextChoices):
        CABALLERO = "caballero", "Caballero"
        DAMA = "dama", "Dama"
        ARABE = "arabe", "Arabe"

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120)
    description = models.TextField()
    notes = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=200, blank=True)
    catalog = models.CharField(max_length=20, choices=Catalog.choices, default=Catalog.CABALLERO)
    main_chords = models.ManyToManyField('Main_chords', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    grams = models.IntegerField(default=100)
    gram_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.brand} {self.name}"

    @property
    def image_url(self):
        return related_image_url(self.images)



class Main_chords(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name



class Container(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=200)
    size = models.CharField(max_length=200)
    weight = models.CharField(max_length=200)
    volume = models.CharField(max_length=200)
    material = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    main_chords = models.ManyToManyField('Main_chords', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        return related_image_url(self.images)


class PerfumeImage(models.Model):
    perfume = models.ForeignKey(
        "perfumes.Perfume",
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="perfumes/",
    )

    alt_text = models.CharField(
        max_length=150,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Imagen de {self.perfume}"


@receiver(post_delete, sender=PerfumeImage)
def remove_perfume_image_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


class EnvaseImage(models.Model):
    container = models.ForeignKey(
        "perfumes.Container",
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="containers/",
    )

    alt_text = models.CharField(
        max_length=150,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Imagen de {self.container}"