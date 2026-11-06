from django.contrib import admin
from .models import Vehicle, VehicleImage, Venue, VenueImage

class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region", "capacity", "price_from", "is_published")
    list_filter = ("country", "is_published")
    search_fields = ("name", "region")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VenueImageInline]

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "model", "vehicle_type", "daily_price", "is_available")
    list_filter = ("vehicle_type", "is_available")
    inlines = [VehicleImageInline]
