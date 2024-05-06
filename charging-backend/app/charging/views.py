from django.contrib.auth.models import User
from rest_framework import permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from django.utils import timezone
from django.shortcuts import get_object_or_404

from app.charging.models import Station, Booking
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
        user = User.objects.first()
        booking = BookingSerializer(user.booking).data if hasattr(user, 'booking') else None
        charging_status = user.charging_sessions.filter(end_time=None).first()
        return Response(data={
            'booking': booking,
            'charging_status': ChargingSessionSerializer(charging_status).data,
            'stations':StationSerializer(Station.objects.all(), many=True).data
            })


class StationBookView(APIView):

    def post(self, request, *args, **kwargs):
        id = kwargs["id"]
        user = User.objects.first()
        station = get_object_or_404(Station, id=id)
        station.book(user)
        booking = BookingSerializer(user.booking).data if hasattr(
            user, 'booking') else None
        return Response(
            data={
                'booking':
                booking,
                'stations':
                StationSerializer(Station.objects.all(), many=True).data
            })

class StationLeaveBookingView(APIView):

    def post(self, request, *args, **kwargs):
        user = User.objects.first()
        booking = get_object_or_404(Booking, user=user)
        booking.delete()
        return Response(
            StationSerializer(Station.objects.all(), many=True).data
        )


class StartChargingView(APIView):

    def post(self, request, *args, **kwargs):
        user = User.objects.first()
        # Check if user has booking
        booking = Booking.objects.filter(user=user).first()
        if not booking:
            return Response('You need to book before charging', status=status.HTTP_400_BAD_REQUEST)
        if not booking:
            return Response('You need to book before charging',
                            status=status.HTTP_400_BAD_REQUEST)
        session = booking.start_charging()
        if isinstance(session, str):
            return Response(session, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            data={
                'charging_status':
                ChargingSessionSerializer(session).data,
                'stations':
                StationSerializer(Station.objects.all(), many=True).data
            })


class StopChargingView(APIView):

    def post(self, request, *args, **kwargs):
        user = User.objects.first()
        charging = user.charging_sessions.filter(end_time=None).first()
        if charging:
            charging.stop_charging()
        return Response(
            StationSerializer(Station.objects.all(), many=True).data)
