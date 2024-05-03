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
        # Avoid booking while charging
        if user.charging_sessions.filter(end_time=None).first():
            return
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

    def delete(self):
        self.remove_from_list()
        super(Booking, self).delete()
        
    def remove_from_list(self):
        bookings = Booking.objects.filter(station=self.station, position__gt=self.position).order_by('position')
        for book in bookings:
            book.position-=1
            book.save()

    def start_charging(self):
        if self.station.available_chargers() <= self.position:
            return 'Not your turn'
        if self.user.charging_sessions.filter(end_time=None).first():
            return 'You cant charge while already charging'
        # Get available Charger
        available_charger = Charger.objects.filter(station =self.station, status=ChargerStatus.AVAILABLE).first()
        available_charger.status = ChargerStatus.OCCUPIED
        available_charger.save()

        charging_session = ChargingSession.objects.create(user=self.user, charger=available_charger)
        self.delete()
        return charging_session
class ChargingSession(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='charging_sessions')
    charger = models.ForeignKey(Charger, null=False, on_delete=models.CASCADE)

    # Time
    start_time = models.DateTimeField(null=False, blank=False, default=timezone.now)
    threshold_breach_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Percent and price
    price = models.IntegerField(null=True, blank=True)
    percent = models.FloatField(null=True, blank=True)

    def current_price(self):
        sub_threshold_time = timezone.now()- self.start_time 
        if self.threshold_breach_time:
             sub_threshold_time = self.threshold_breach_time- self.start_time
        elif self.end_time:
            sub_threshold_time = self.end_time - self.start_time 
        sub_threshold_time = (sub_threshold_time.total_seconds() / 60)
        threshold_time = 0

        if self.threshold_breach_time:
            threshold_time = self.end_time - self.threshold_breach_time if self.end_time else (timezone.now() - self.threshold_breach_time)
            threshold_time  = threshold_time.total_seconds() / 60
        return 10*sub_threshold_time + 20*threshold_time

    def save(self, *args: tuple, **kwargs: dict):
        self.price = self.current_price()
        super().save(*args, **kwargs)
