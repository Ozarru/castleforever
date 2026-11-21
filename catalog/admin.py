from django.contrib import admin
from .models import Vehicle, VehicleImage, Estate, EstateImage

class EstateImageInline(admin.TabularInline):
    model = EstateImage
    extra = 1

@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ("name", "estate_type", "country", "region", "city", "capacity", "price_from", "is_published")
    list_filter = ("estate_type", "country", "is_published")
    search_fields = ("name", "region", "city", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [EstateImageInline]

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "model", "vehicle_type", "daily_price", "is_available")
    list_filter = ("vehicle_type", "is_available")
    inlines = [VehicleImageInline]
