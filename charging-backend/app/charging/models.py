from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.utils import timezone

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
        return self.booking_set.count()

    def __str__(self):
        return self.name

    def book(self, user):
        booking = Booking.objects.filter(user=user).first()
        queue = Booking.objects.filter(station=self).order_by('position')
        if not booking:
            Booking.objects.create(user=user, station=self, position = len(queue)+1)
        elif booking.station != self:
            booking.remove_from_list()
            booking.station = self
            booking.position = len(queue)+1
            booking.save()





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

class Booking(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, null=False, on_delete=models.CASCADE)
    
    position = models.PositiveIntegerField(null=True, blank=True)
    register_time = models.DateTimeField(null=False, blank=False, default=timezone.now)

    def save(self, *args: tuple, **kwargs: dict):
        super().save(*args, **kwargs)

    def delete(self):
        self.remove_from_list()
        super(Booking, self).delete()
        
    def remove_from_list(self):
        bookings = Booking.objects.filter(station=self.station, position__gt=self.position).order_by('position')
        for book in bookings:
            book.position-=1
            book.save()