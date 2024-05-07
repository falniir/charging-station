from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.utils import timezone

def get_profile(user: User):
    return Profile.objects.get_or_create(user=user)[0]

def get_mock_user():
    return User.objects.all().first()

def get_mock_chargingsession():
    return get_mock_user().charging_sessions.filter(end_time=None).first()


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
        # ref: profilestate, TRANSISTION IDLE/BOOKING to BOOKING
        profile = get_profile(user)
        if profile.wallet <= 0:
            return 'Insufficent funds'
        if not profile.state not in [ProfileState.IDLE, ProfileState.BOOKING]:
            return 'Cant book while charging'
        profile.state = ProfileState.BOOKING
        # ref: profilestate, ENTRY to BOOKING
        Booking.enter_queue(user, self)
        return Booking.enter_queue(user, self)

    def reserve_charger(self):
        # ref: profilestate, entry RESERVING
        # ref: chargerstate_backend: Transistion from AVAILABLE to OCCUPIED
        available_charger = Charger.objects.filter(
            station=self.station, state=ChargerState.AVAILABLE).first()
        available_charger.set_occupied()
        available_charger.state = ChargerState.OCCUPIED
        available_charger.save()

        return available_charger



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
        self.clear_connections()
        self.state = ChargerState.BROKEN
        self.save()

    def stop_session(self):
        # ref: chargerstate_backend: BROKEN entry method
        running = ChargingSession.objects.filter(end_time=None,
                                                 charger=self).first()
        if running:
            running.stop_charging()

    def set_fixed(self):
        # ref: chargerstate_backend: Transistion BROKEN to AVAILABLE
        if self.state == ChargerState.BROKEN:
            self.state = ChargerState.AVAILABLE
            self.save()

    def free_charger(self):
        # ref: profilestate: EXIT CHARGING
        # ref: chargerstate_backend: Transistion OCCUPIED to AVAILABLE
        self.state = ChargerState.AVAILABLE
        self.save()

class Booking(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, null=False, on_delete=models.CASCADE)

    position = models.PositiveIntegerField(null=True, blank=True)
    register_time = models.DateTimeField(null=False,
                                         blank=False,
                                         default=timezone.now)

    def cancel_booking(self):
        # ref: profilestate, TRANSISTION of BOOKING to IDLE
        profile = get_profile(self.user)
        if profile.state == ProfileState.BOOKING:
            profile = get_profile(self.user)
            profile.state = ProfileState.IDLE
            profile.save()
            self.remove_from_queue()
        self.delete()

    @staticmethod
    def enter_queue(user: User, station: Station):
        # ref: profilestate, ENTRY to BOOKING
        booking = Booking.objects.filter(user=user).first()
        queue = Booking.objects.filter(station=station).order_by('position')
        if not booking:
            booking = Booking.objects.create(user=user,
                                             station=station,
                                             position=len(queue) + 1)
        elif booking.station != station:
            booking.remove_from_queue()
            booking.station = station
            booking.position = len(queue) + 1
            booking.save()
        return booking

    def remove_from_queue(self):
        # ref: profilestate, exit FROM BOOKING to IDLE
        # ref: profilestate, entry RESERVING
        bookings = Booking.objects.filter(
            station=self.station,
            position__gt=self.position).order_by('position')
        for book in bookings:
            book.position -= 1
            book.save()

    def reserve_charging(self):
        # ref: profilestate, TRANSISTION from BOOKING to RESERVING
        profile = get_profile(self.user)
        # Conditions to return messages if not correct conditions are set.
        if self.user.charging_sessions.filter(
                end_time=None).first() or profile.state in [
                    ProfileState.RESERVING, ProfileState.CHARGING
                ]:
            return 'Already reserved'
        if self.station.available_chargers() <= self.position:
            return 'Not your turn'

        # ref: chargerstate_backend: Transistion from AVAILABLE to OCCUPIED
        # ref: profilestate, entry RESERVING
        # Get available Charger
        available_charger = self.station.reserve_charger()

        # ref: profilestate: Transistion from AVAILABLE to OCCUPIED
        charging_session = ChargingSession.objects.create(
            user=self.user, charger=available_charger)
        profile.state = ProfileState.RESERVING
        profile.save()

        # ref: profilestate, ENTRY to RESERVED
        self.remove_from_queue()
        self.delete()
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
    price = models.FloatField(null=True, blank=True)
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
        if self.state not in [
                ChargingSessionState.OVERCHARGING,
                ChargingSessionState.CHARGING
        ]:
            return
        self.stop_charging()

    def set_connected(self):
        # ref: profilestate: Transistion from RESERVING to CHARGING
        profile = get_profile(self.user)
        if profile.state == ProfileState.RESERVING:
            profile.state = ProfileState.CHARGING
            profile.save()
            # ref: profilestate: ENTRY to CHARGING
            self.start_charging()

    def start_charging(self):
        # ref: profilestate: ENTRY to CHARGING
        # ref: chargingsessionstate: Transistion from NOT_CONNECTED to CHARGING
        self.state = ChargingSessionState.CHARGING
        self.save()
        self.set_start_time()

    def update_percent(self, percent):
        # ref: profilestate: INTERNAL TRANSISTION CHARGING
        self.percent = percent
        if self.percent >= 80 and self.state == ChargingSessionState.CHARGING:
            self.threshold_breached()
        else:
            self.save()
        if 99.9 < self.percent:
            self.stop_charging()

    def threshold_breached(self):
        # ref: chargingsessionstate: Transistion from CHARGING to OVERCHARGING
        self.state = ChargingSessionState.OVERCHARGING
        self.save()
        self.set_threshold_breached_time()

    def set_start_time(self):
        # ref: chargingsessionstate: ENTRY to CHARGING
        self.start_time = timezone.now()
        self.save()

    def set_threshold_breached_time(self):
        # ref: chargingsessionstate: ENTRY to OVERCHARGING
        self.threshold_breach_time = timezone.now()
        self.save()

    def stop_charging(self):
        # ref: profilestate: Transistion from CHARGING to IDLE
        # ref: profilestate: EXIT CHARGING
        self.charger.free_charger()

        # ref: chargingsessionsstate: Transistion from CHARGING/OVERCHARGING to COMPLETED/COMPLETED,OVERCHARGING
        self.state = ChargingSessionState.COMPLETED if not self.state == ChargingSessionState.OVERCHARGING else ChargingSessionState.COMPLETED_OVERCHARGED
        self.save()
        self.set_endtime()

        profile = get_profile(self.user)
        profile.state = ProfileState.IDLE
        profile.save()
        # ref: profilestate: EXIT CHARGING
        self.pay_for_charging()

    def set_endtime(self):
        self.end_time = timezone.now()
        self.save()

    def cancel_reservation(self):
        # ref: profilestate: Transistion from RESERVED to IDLE
        # ref: profilestate: EXIT RESERVED to IDLE
        self.charger.free_charger()

        profile = get_profile(self.user)
        profile.state = ProfileState.IDLE
        profile.save()
        self.delete()

    def pay_for_charging(self):
        # ref: profilestate: EXIT CHARGING
        profile = get_profile(self.user)
        profile.wallet -= self.price
        profile.save()

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
    IDLE = 0, _('Idle')
    BOOKING = 1, _('Booking')
    RESERVING = 2, _('Reserving')
    CHARGING = 3, _('Charging')


class Profile(models.Model):
    user = models.OneToOneField(User,
                                null=False,
                                on_delete=models.CASCADE,
                                related_name="profile")
    state = models.IntegerField(null=True,
                                choices=ProfileState.choices,
                                default=ProfileState.IDLE)
    wallet = models.IntegerField(null=True, blank=True, default=0)
