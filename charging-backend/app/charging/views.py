from django.contrib.auth.models import User
from rest_framework import permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from django.utils import timezone
from django.conf import settings
from app.charging.mqtt import client as mqtt_client

from django.shortcuts import get_object_or_404

from app.charging.models import Station, Booking, get_profile, get_mock_user, ProfileState
from app.charging.serializers import StationSerializer, BookingSerializer, ChargingSessionSerializer


class StationsView(viewsets.ModelViewSet):
    """
        View to view all stations
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']


class StationUserView(APIView): # Dashboard
    """
        Dashboard view go get all necessary info
    """
    def get(self, request, *args, **kwargs):
        # Use mock user
        user = get_mock_user() if request.user.is_anonymous else request.user
        # get booking info, if it is booking
        booking = BookingSerializer(user.booking).data if hasattr(
            user, 'booking') else None
        
        # Get chargingsession, or previous charging session
        charging_status = user.charging_sessions.filter(end_time=None).first()
        if not charging_status:
            charging_status = user.charging_sessions.order_by('-end_time').first()

        # return current funds
        funds = get_profile(user).wallet
        return Response(
            data={'funds': funds,
                'booking':
                booking,
                'charging_status':
                ChargingSessionSerializer(charging_status).data,
                'stations':
                StationSerializer(Station.objects.all(), many=True).data
            })


class StationBookView(APIView):

    def post(self, request, *args, **kwargs):
        # get id of station
        id = kwargs["id"]
        # mock user for test
        user = get_mock_user() if request.user.is_anonymous else request.user
        # check if station exists
        station = get_object_or_404(Station, id=id)
        # book
        booking = station.book(user)
        # check for error messages
        if isinstance(booking, str):
            return Response(booking, status=status.HTTP_400_BAD_REQUEST)
        booking = BookingSerializer(user.booking).data

        return Response(
            data={
                'booking':
                booking,
                'stations':
                StationSerializer(Station.objects.all(), many=True).data
            })

class StationCancelBookingView(APIView):

    def post(self, request, *args, **kwargs):
        # cancel current booking for user
        user = get_mock_user() if request.user.is_anonymous else request.user
        booking = get_object_or_404(Booking, user=user)
        booking.cancel_booking()
        return Response(
            StationSerializer(Station.objects.all(), many=True).data
        )


class StartChargingView(APIView):

    def post(self, request, *args, **kwargs):
        # get user
        user = get_mock_user() if request.user.is_anonymous else request.user
        # Check if user has booking
        booking = Booking.objects.filter(user=user).first()
        # if no booking, dont charge
        if not booking:
            return Response('You need to book before charging',
                            status=status.HTTP_400_BAD_REQUEST)
        # create session
        session = booking.reserve_charging()
        # if error return them
        if isinstance(session, str):
            return Response(session, status=status.HTTP_400_BAD_REQUEST)
        # send to charger it is reserved
        r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'RESERVE',qos=1)
        print(r, c)

        return Response(
            data={
                'charging_status':
                ChargingSessionSerializer(session).data,
                'stations':
                StationSerializer(Station.objects.all(), many=True).data
            })


class StopChargingView(APIView):

    def post(self, request, *args, **kwargs):
        # send message to charger it should stop being reserved and charge
        user = get_mock_user() if request.user.is_anonymous else request.user
        charging = user.charging_sessions.filter(end_time=None).first()
        profile = get_profile(user)
        # if it is charging, stop charging
        if profile.state == ProfileState.CHARGING:
            charging.stop_charging()
            r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'STOP', qos=1)
        elif profile.state == ProfileState.RESERVING:
            # if it is only reserved, stop charging
            charging.cancel_reservation()
            r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'STOP',qos=1)
        return Response(
            StationSerializer(Station.objects.all(), many=True).data)
