from django.contrib import admin
from app.charging.models import Station, Booking, Charger
# Register your models here.
@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'name', 'total_chargers']
    list_display = ['id', 'name', 'total_chargers']
    search_fields = ['id', 'name', 'total_chargers']
@admin.register(Charger)
class ChargerAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'station', 'status']
    list_display = ['id', 'station', 'status']
    search_fields = ['id', 'station','status']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'user','station', 'position']
    list_display = ['id', 'user','station', 'position']
    search_fields = ['id', 'user','station', 'position']