from django.contrib import admin
from app.charging.models import Station, Booking, Charger, ChargingSession, Profile, ChargerState
from django.conf import settings
from app.charging.mqtt import client as mqtt_client
# Register your models here.
@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'name', 'total_chargers']
    list_display = ['id', 'name', 'total_chargers']
    search_fields = ['id', 'name', 'total_chargers']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'user','station', 'position']
    list_display = ['id', 'user','station', 'position']
    search_fields = ['id', 'user','station', 'position']

@admin.action(description="Set Charger to broken")
def set_broken(modeladmin, request, queryset):
    queryset.update(state=ChargerState.BROKEN)
    # set charger to broken
    r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'MAINTANENCE', qos=1)
    print(r, c)

@admin.action(description="Set Charger to fixed")
def set_fixed(modeladmin, request, queryset):
    queryset = queryset.filter(state=ChargerState.BROKEN)
    queryset.update(state=ChargerState.AVAILABLE)
    # set charger to fixed
    r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'RESET', qos=1)
    print(r, c)

@admin.register(Charger)
class ChargerAdmin(admin.ModelAdmin):
    sortable_by = ['id', 'station', 'state']
    list_display = ['id', 'station', 'state']
    search_fields = ['id', 'station','state']
    actions = [set_broken, set_fixed]


@admin.register(ChargingSession)
class ChargingSessionAdmin(admin.ModelAdmin):
    sortable_by = ['user', 'charger', 'start_time', 'price', 'percent', 'state']
    list_display = ['user', 'charger', 'start_time', 'price', 'percent', 'state']
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    sortable_by = ['user','wallet', 'state']
    list_display = ['user','wallet', 'state']