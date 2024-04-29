from django.contrib.auth.models import User
from rest_framework import permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404

from app.charging.models import Station
from app.charging.serializers import StationSerializer

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


class StationBookView(APIView):

    def post(self, request, *args, **kwargs):
        id = kwargs["id"]
        user = User.objects.first()
        station = get_object_or_404(Station, id=id)
        station.book(user)
        Station.objects.all()
        return Response(data=StationSerializer(Station.objects.all(), many=True).data)