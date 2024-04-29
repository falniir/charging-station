from django.core.management.base import BaseCommand
from app.charging.models import Station, Charger
import random

stations =  [
  {
    'name': 'Shell Klæbu',
  },
  {
    'name': 'Shell Midtbyen',
  },
  {
    'name': 'Exxon Nidarosdomen',
  },
  {
    'name': 'Statoil Samfundet',
  },
  {
    'name': 'YX Kjøpmannsgata',
  },
]


class Command(BaseCommand):
    help = 'Fill DB'

    def handle(self, *args, **options):
        Station.objects.all().delete()
        for station in stations:
            new_station = Station.objects.create(name=station['name'])
            for i in range(random.randint(2, 10)):
                Charger.objects.create(station=new_station)
        self.stdout.write(self.style.SUCCESS('Successfully created Stations and Chargers'))
