from django.db import models


class Perfume(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120)
    description = models.TextField()
    notes = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=200, blank=True)
    main_chords = models.ManyToManyField('Main_chords', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    image_url = models.URLField(max_length=500)
    type = models.CharField(max_length=200)
    size = models.CharField(max_length=200)
    weight = models.CharField(max_length=200)
    volume = models.CharField(max_length=200)
    material = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    main_chords = models.ManyToManyField('Main_chords', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


        