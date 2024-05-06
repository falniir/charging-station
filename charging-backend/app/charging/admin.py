from django.contrib import admin
from app.charging.models import Station, Booking, Charger, ChargingSession, Profile
# Register your models here.
@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'name', 'total_chargers']
    list_display = ['id', 'name', 'total_chargers']
    search_fields = ['id', 'name', 'total_chargers']
@admin.register(Charger)
class ChargerAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'station', 'state']
    list_display = ['id', 'station', 'state']
    search_fields = ['id', 'station','state']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'user','station', 'position']
    list_display = ['id', 'user','station', 'position']
    search_fields = ['id', 'user','station', 'position']

@admin.register(ChargingSession)
class ChargingSessionAdmin(admin.ModelAdmin):
    sortable_by = ['user', 'charger', 'start_time', 'price']
    list_display = ['user', 'charger', 'start_time', 'price']
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    sortable_by = ['user','wallet']
    list_display  = ['user','wallet']