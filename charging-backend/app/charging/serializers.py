from django.contrib.auth.models import User
from rest_framework import serializers
from app.charging.models import Station, Booking

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