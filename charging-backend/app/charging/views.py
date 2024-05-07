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

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class StationsView(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']


class StationUserView(APIView):

    def get(self, request, *args, **kwargs):
        user = get_mock_user() if request.user.is_anonymous else request.user
        booking = BookingSerializer(user.booking).data if hasattr(
            user, 'booking') else None
        charging_status = user.charging_sessions.filter(end_time=None).first()
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
        id = kwargs["id"]
        user = get_mock_user() if request.user.is_anonymous else request.user
        station = get_object_or_404(Station, id=id)
        booking = station.book(user)
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
        user = get_mock_user() if request.user.is_anonymous else request.user
        booking = get_object_or_404(Booking, user=user)
        booking.cancel_booking()
        return Response(
            StationSerializer(Station.objects.all(), many=True).data
        )


class StartChargingView(APIView):

    def post(self, request, *args, **kwargs):
        user = get_mock_user() if request.user.is_anonymous else request.user
        # Check if user has booking
        booking = Booking.objects.filter(user=user).first()
        if not booking:
            return Response('You need to book before charging',
                            status=status.HTTP_400_BAD_REQUEST)
        session = booking.reserve_charging()
        if isinstance(session, str):
            return Response(session, status=status.HTTP_400_BAD_REQUEST)

        r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'RESERVE')
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
        user = get_mock_user() if request.user.is_anonymous else request.user
        charging = user.charging_sessions.filter(end_time=None).first()
        profile = get_profile(user)
        if profile.state == ProfileState.CHARGING:
            charging.stop_charging()
            r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'STOP')
        elif profile.state == ProfileState.RESERVING:
            charging.cancel_reservation()
            r, c = mqtt_client.publish(settings.MQTT_TOPIC, 'STOP')
        return Response(
            StationSerializer(Station.objects.all(), many=True).data)
