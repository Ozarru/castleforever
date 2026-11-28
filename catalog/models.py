from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _


class Estate(models.Model):
    class Country(models.TextChoices):
        FR = "FR", _("France")
        IT = "IT", _("Italy")
        ES = "ES", _("Spain")
        DE = "DE", _("Germany")
        PT = "PT", _("Portugal")

    class EstateType(models.TextChoices):
        CASTLE = "castle", _("Castles")
        PALACE = "palace", _("Palaces")
        VILLA = "villa", _("Villas")
        MANOR = "manor", _("Manors")
        GARDEN = "garden", _("Gardens & Terraces")

    # Kept as module-level aliases because other apps read these directly.
    COUNTRY_CHOICES = Country.choices
    ESTATE_TYPE_CHOICES = EstateType.choices

    name = models.CharField(_("Name"), max_length=180)
    slug = models.SlugField(_("Slug"), unique=True, max_length=200)
    estate_type = models.CharField(
        _("Estate type"),
        max_length=12,
        choices=EstateType.choices,
        default=EstateType.CASTLE,
    )
    country = models.CharField(_("Country"), max_length=2, choices=Country.choices)
    region = models.CharField(_("Region"), max_length=120)
    city = models.CharField(
        _("City"),
        max_length=120,
        blank=True,
        help_text=_("Nearest city or town, used in public search."),
    )
    description = models.TextField(_("Description"))
    description_fr = models.TextField(_("Description (French)"), blank=True)
    description_es = models.TextField(_("Description (Spanish)"), blank=True)
    description_it = models.TextField(_("Description (Italian)"), blank=True)
    description_de = models.TextField(_("Description (German)"), blank=True)
    description_pt = models.TextField(_("Description (Portuguese)"), blank=True)
    capacity = models.PositiveIntegerField(_("Capacity"), validators=[MinValueValidator(1)])
    price_from = models.DecimalField(
        _("Price from"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    cover_image = models.ImageField(
        _("Cover image"),
        upload_to="estates/",
        blank=True,
        help_text=_("Optional uploaded cover image"),
    )
    cover_image_url = models.URLField(
        _("Cover image URL"),
        blank=True,
        help_text=_("Optional remote image for initial catalog"),
    )
    is_published = models.BooleanField(_("Published"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        ordering = ["country", "name"]
        indexes = [
            models.Index(fields=["is_published", "country"], name="estate_pub_country_idx"),
            models.Index(fields=["estate_type"], name="estate_type_idx"),
        ]
        verbose_name = _("Estate")
        verbose_name_plural = _("Estates")

    def __str__(self):
        return self.name

    def description_for(self, language_code=None):
        """Return the description for a language, falling back to English."""
        code = (language_code or get_language() or "en").split("-")[0]
        if code == "en":
            return self.description
        return getattr(self, f"description_{code}", "") or self.description

    @property
    def localized_description(self):
        return self.description_for()

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url

    def get_absolute_url(self):
        return reverse("catalog:estate-detail", kwargs={"slug": self.slug})


class EstateImage(models.Model):
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="estates/", blank=True)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "pk"]

    @property
    def url(self):
        return self.image.url if self.image else self.image_url

    def __str__(self):
        return f"{self.estate.name} photo {self.position + 1}"


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
    vehicle_type = models.CharField(
        max_length=20, choices=Category.choices, default=Category.EXOTIC)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.EXOTIC)
    color = models.CharField(max_length=60, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="vehicles/",
                              blank=True, help_text="Optional uploaded image")
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
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="images")
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
        return f"{self.vehicle.name} photo {self.position + 1}"
