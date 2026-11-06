from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Venue(models.Model):
    COUNTRY_CHOICES = [("FR", "France"), ("IT", "Italy"), ("ES", "Spain")]
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, max_length=200)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    region = models.CharField(max_length=120)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    price_from = models.DecimalField(max_digits=12, decimal_places=2)
    cover_image = models.ImageField(upload_to="venues/", blank=True, help_text="Optional uploaded cover image")
    cover_image_url = models.URLField(blank=True, help_text="Optional remote image for initial catalog")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url

    def get_absolute_url(self):
        return reverse("catalog:venue-detail", kwargs={"slug": self.slug})

class VenueImage(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="venues/", blank=True)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "pk"]

    @property
    def url(self):
        return self.image.url if self.image else self.image_url

class Vehicle(models.Model):
    class Category(models.TextChoices):
        EXOTIC = "exotic", "Exotic car"
        LIMOUSINE = "limousine", "Limousine"
        SUV = "suv", "SUV"
        SEDAN = "sedan", "Sedan"
        OTHER = "other", "Other"

    name = models.CharField(max_length=180)
    brand = models.CharField(max_length=120, blank=True)
    model = models.CharField(max_length=120, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=Category.choices, default=Category.EXOTIC)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.EXOTIC)
    color = models.CharField(max_length=60, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="vehicles/", blank=True, help_text="Optional uploaded image")
    image_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.name


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="vehicles/", blank=True)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "pk"]

    @property
    def url(self):
        return self.image.url if self.image else self.image_url

    def __str__(self):
        return f"{self.vehicle.name} photo"
