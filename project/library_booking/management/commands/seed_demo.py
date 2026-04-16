from django.core.management.base import BaseCommand

from library_booking.models import ComputerPlace, Status, StatusCodes, StatusKind


class Command(BaseCommand):
    help = 'Создаёт демо-места, если таблица пуста (после migrate).'

    def handle(self, *args, **options):
        if ComputerPlace.objects.exists():
            self.stdout.write('Компьютерные места уже есть — пропуск.')
            return
        available = Status.objects.get(
            code=StatusCodes.PLACE_AVAILABLE,
            kind=StatusKind.PLACE,
        )
        unavailable = Status.objects.get(
            code=StatusCodes.PLACE_UNAVAILABLE,
            kind=StatusKind.PLACE,
        )
        rows = [
            dict(number=1, zone='Зона А', operating_system='Windows 11', status=available),
            dict(number=2, zone='Зона А', operating_system='Ubuntu', status=available),
            dict(number=1, zone='Зона Б', operating_system='Windows 11', status=unavailable),
            dict(number=3, zone='Зона А', operating_system='Windows 11', status=available),
        ]
        for r in rows:
            ComputerPlace.objects.create(**r)
        self.stdout.write(self.style.SUCCESS('Демо-места созданы.'))
