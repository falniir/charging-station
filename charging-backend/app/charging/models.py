from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class ChargerStatus(models.IntegerChoices):
    AVAILABLE = 0, _('Available')
    OCCUPIED = 1, _('Occupied')
    BROKEN = 2, _('Broken')


class Station(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True)

    def available_chargers(self):
        return self.chargers.filter(status=ChargerStatus.AVAILABLE).count()

    def total_chargers(self):
        return self.chargers.exclude(status=ChargerStatus.BROKEN).count()

    def queue_count(self):
        return self.booked_by.count()

    def __str__(self):
        return self.name

    def book(self, user):
        profile = Profile.objects.get_or_create(user=user)[0]
        profile.booked_station = self
        profile.save()



class Charger(models.Model):
    status = models.IntegerField(null=True,
                                 choices=ChargerStatus.choices,
                                 default=ChargerStatus.AVAILABLE)
    station = models.ForeignKey(Station,
                                null=False,
                                blank=False,
                                on_delete=models.CASCADE,
                                related_name='chargers')

    def __str__(self):
        return f'{self.station.name} {self.id}'

class Profile(models.Model):
    # Dont create a new model to extend user to, instead add a profile
    # Simplifies the process
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    booked_station = models.ForeignKey(Station, null=True, on_delete=models.SET_NULL, related_name="booked_by")
