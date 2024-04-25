from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from .serializers import UserSerializer

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