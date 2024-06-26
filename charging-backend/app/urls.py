"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app.charging import views as ChargingViews
from rest_framework import routers
from app import views as MQTTViews

router = routers.DefaultRouter()
router.register('stations', ChargingViews.StationsView)
urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/user/', ChargingViews.StationUserView.as_view()),
    path('booking/book/<int:id>/', ChargingViews.StationBookView.as_view()),
    path('booking/start_charging/', ChargingViews.StartChargingView.as_view()),
    path('booking/stop_charging/', ChargingViews.StopChargingView.as_view()),
    path('booking/leave_booking/', ChargingViews.StationCancelBookingView.as_view()),
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('publish', MQTTViews.publish_message, name='publish'),
]
