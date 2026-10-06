from django.db import models


class Perfume(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120)
    description = models.TextField()
    notes = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=200, blank=True)
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