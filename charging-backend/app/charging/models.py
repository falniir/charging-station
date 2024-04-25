from django.db import models
from django.utils.translation import gettext as _

class ChargerStatus(models.IntegerChoices):
    AVAILABLE = 0, _('Available')
    OCCUPIED = 1, _('Occupied')
    BROKEN = 2, _('Broken')


class Station(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True)
    queue_count = models.PositiveIntegerField(null=True, blank=True, default=0)

    def available_chargers(self):
        return self.chargers.filter(status=ChargerStatus.AVAILABLE).count()

    def total_chargers(self):
        return self.chargers.exclude(status=ChargerStatus.BROKEN).count()

    def __str__(self):
        return self.name


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