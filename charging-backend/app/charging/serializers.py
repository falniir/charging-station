from django.contrib.auth.models import User
from rest_framework import serializers
from app.charging.models import Station, Booking, ChargingSession

class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']



class StationSerializer(serializers.ModelSerializer):
    total_chargers = serializers.SerializerMethodField(
        method_name='get_total_chargers', read_only=True)
    available_chargers = serializers.SerializerMethodField(
        method_name='get_available_chargers', read_only=True)
    queue_count = serializers.SerializerMethodField(
        method_name='get_queue_count', read_only=True)
    class Meta:
        model = Station
        fields = [
            'id', 'name', 'queue_count', 'total_chargers', 'available_chargers'
        ]

    def get_total_chargers(self, station):
        return station.total_chargers()

    def get_queue_count(self, station):
        return station.queue_count()

    def get_available_chargers(self, station):
        return station.available_chargers()
    
class BookingSerializer(serializers.ModelSerializer):
    station = StationSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ['position', 'station', 'register_time']

class ChargingSessionSerializer(serializers.ModelSerializer):
    charger = serializers.SerializerMethodField(
        method_name='get_charger', read_only=True)
    price = serializers.SerializerMethodField(
        method_name='get_price', read_only=True)
    def get_price(self, chargingSession):
        return chargingSession.current_price()
    
    def get_charger(self, chargingSession):
        return chargingSession.charger.__str__()

    class Meta:
        model = ChargingSession
        fields = ['charger', 'start_time', 'price', 'percent', 'state']