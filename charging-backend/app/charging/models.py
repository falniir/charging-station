from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.utils import timezone

def get_profile(user: User):
    return Profile.objects.get_or_create(user=user)[0]


class Station(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True)

    def available_chargers(self):
        return self.chargers.filter(state=ChargerState.AVAILABLE).count()

    def total_chargers(self):
        return self.chargers.exclude(state=ChargerState.BROKEN).count()

    def queue_count(self):
        return self.booking_set.count()

    def __str__(self):
        return self.name

    def book(self, user):
        # Avoid booking while charging
        if get_profile(user).wallet <= 0:
            return 'Insufficent funds'
        if user.charging_sessions.filter(end_time=None).first():
            return 'Cant book while charging'
        booking = Booking.objects.filter(user=user).first()
        queue = Booking.objects.filter(station=self).order_by('position')
        if not booking:
            Booking.objects.create(user=user,
                                   station=self,
                                   position=len(queue) + 1)
        elif booking.station != self:
            booking.remove_from_list()
            booking.station = self
            booking.position = len(queue) + 1
            booking.save()
        return booking




class ChargerState(models.IntegerChoices):
    # State of a charger, either available, occupied or broken
    AVAILABLE = 0, _('Available')
    OCCUPIED = 1, _('Occupied')
    BROKEN = 2, _('Broken')


class Charger(models.Model):
    state = models.IntegerField(null=True,
                                choices=ChargerState.choices,
                                default=ChargerState.AVAILABLE)
    station = models.ForeignKey(Station,
                                null=False,
                                blank=False,
                                on_delete=models.CASCADE,
                                related_name='chargers')

    def __str__(self):
        return f'{self.station.name} {self.id}'

    def set_broken(self):
        # ref: chargerstate_backend: Transistion AVAILABLE/OCCUPIED to BROKEN
        self.state = ChargerState.BROKEN
        self.save()

    def set_fixed(self):
        # ref: chargerstate_backend: Transistion BROKEN to AVAILABLE
        if self.state == ChargerState.BROKEN:
            self.state = ChargerState.AVAILABLE
            self.save()


class Booking(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, null=False, on_delete=models.CASCADE)

    position = models.PositiveIntegerField(null=True, blank=True)
    register_time = models.DateTimeField(null=False,
                                         blank=False,
                                         default=timezone.now)

    def delete(self):
        self.remove_from_list()
        super(Booking, self).delete()

    def remove_from_list(self):
        bookings = Booking.objects.filter(
            station=self.station,
            position__gt=self.position).order_by('position')
        for book in bookings:
            book.position -= 1
            book.save()

    def start_charging(self):
        # Conditions to return messages if not correct conditions are set.
        if self.user.charging_sessions.filter(end_time=None).first():
            return 'Already charging'
        if self.station.available_chargers() <= self.position:
            return 'Not your turn'
        if self.user.charging_sessions.filter(end_time=None).first():
            return 'You cant charge while already charging'

        # Get available Charger
        available_charger = Charger.objects.filter(
            station=self.station, state=ChargerState.AVAILABLE).first()
        # ref: chargerstate_backend: Transistion from AVAILABLE to OCCUPIED
        available_charger.state = ChargerState.OCCUPIED
        available_charger.save()

        charging_session = ChargingSession.objects.create(
            user=self.user, charger=available_charger)
        self.delete()
        #TODO REMOVE
        charging_session.set_connected()
        return charging_session


class ChargingSessionState(models.IntegerChoices):
    NOT_CONNECTED = 0, _('Not connected')
    CHARGING = 1, _('Charging')
    OVERCHARGING = 2, _('Overcharging')
    COMPLETED = 3, _('Completed')
    COMPLETED_OVERCHARGED = 4, _('Completed overcharged')


class ChargingSession(models.Model):
    # Meta
    state = models.IntegerField(null=True,
                                choices=ChargingSessionState.choices,
                                default=ChargingSessionState.NOT_CONNECTED)
    user = models.ForeignKey(User,
                             null=False,
                             on_delete=models.CASCADE,
                             related_name='charging_sessions')
    charger = models.ForeignKey(Charger, null=False, on_delete=models.CASCADE)

    # Times
    start_time = models.DateTimeField(null=True, blank=True)
    threshold_breach_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    # Percent and prices
    price = models.IntegerField(null=True, blank=True)
    percent = models.FloatField(null=True, blank=True)

    def current_price(self):
        # No price if not connected yet
        if self.state == ChargingSessionState.NOT_CONNECTED: return 0

        sub_threshold_time = timezone.now() - self.start_time
        if self.state in [
                ChargingSessionState.OVERCHARGING,
                ChargingSessionState.COMPLETED_OVERCHARGED
        ]:
            sub_threshold_time = self.threshold_breach_time - self.start_time
        elif self.state == ChargingSessionState.COMPLETED:
            sub_threshold_time = self.end_time - self.start_time
        sub_threshold_time = (sub_threshold_time.total_seconds() / 60)
        threshold_time = 0

        if self.state in [
                ChargingSessionState.OVERCHARGING,
                ChargingSessionState.COMPLETED_OVERCHARGED
        ]:
            threshold_time = self.end_time - self.threshold_breach_time if (
                self.state == ChargingSessionState.COMPLETED_OVERCHARGED
            ) else (timezone.now() - self.threshold_breach_time)
            threshold_time = threshold_time.total_seconds() / 60
        price = 200 * sub_threshold_time + 200 * threshold_time

        if get_profile(self.user).wallet <= price:
            self.cancel_charging(price)
        return price

    def cancel_charging(self, price):
        # Only stop charging if charging
        if self.state not in [
                ChargingSessionState.OVERCHARGING,
                ChargingSessionState.CHARGING
        ]:
            return
        # Update wallet
        profile = get_profile(self.user)
        profile.wallet -= price
        profile.save()

        self.state = ChargingSessionState.COMPLETED if self.state == ChargingSessionState.CHARGING else ChargingSessionState.COMPLETED_OVERCHARGED
        self.end_time = timezone.now()
        self.save()

    def set_connected(self):
        self.start_time = timezone.now()
        self.percent = 70
        if self.percent >= 80:
            self.threshold_breached()
        else:
            self.state = ChargingSessionState.CHARGING
            self.save()

    def update_percent(self):
        if self.percent >= 80:
            self.threshold_breached()

    def threshold_breached(self):
        self.threshold_breach_time = timezone.now()
        self.state = ChargingSessionState.OVERCHARGING
        self.save()

    def stop_charging(self):
        # ref: chargerstate_backend: Transistion OCCUPIED to AVAILABLE
        self.charger.state = ChargerState.AVAILABLE
        self.charger.save()

        # Pay
        profile = get_profile(self.user)
        profile.wallet -= self.price
        profile.save()

        self.end_time = timezone.now()
        self.save()

    def save(self, *args: tuple, **kwargs: dict):
        # Error correction is state is null
        if (not self.state
                or self.state == ChargingSessionState.NOT_CONNECTED):
            if (self.end_time):
                self.state = ChargingSessionState.COMPLETED if not self.threshold_breach_time else ChargingSessionState.COMPLETED_OVERCHARGED
            elif (self.start_time):
                self.state = ChargingSessionState.CHARGING if not self.threshold_breach_time else ChargingSessionState.OVERCHARGING
        self.price = self.current_price()
        super().save(*args, **kwargs)

class ProfileState(models.IntegerChoices):
    IDLE = 0, _('Not connected')


class Profile(models.Model):
    user = models.OneToOneField(User,
                                null=False,
                                on_delete=models.CASCADE,
                                related_name="profile")
    state = models.IntegerField(null=True,
                                choices=ProfileState.choices,
                                default=ProfileState.IDLE)
    wallet = models.IntegerField(null=True, blank=True, default=0)
