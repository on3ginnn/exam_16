from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class StatusKind(models.TextChoices):
    PLACE = 'place', 'Место'
    BOOKING = 'booking', 'Заявка'


class Status(models.Model):
    code = models.SlugField(max_length=50)
    label = models.CharField('Подпись', max_length=100)
    kind = models.CharField('Тип', max_length=10, choices=StatusKind.choices)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        constraints = [
            models.UniqueConstraint(fields=('code', 'kind'), name='uniq_status_code_kind'),
        ]

    def __str__(self):
        return f'{self.label} ({self.get_kind_display()})'


class ComputerPlace(models.Model):
    number = models.PositiveIntegerField('Номер')
    zone = models.CharField('Зона', max_length=100)
    operating_system = models.CharField('Операционная система', max_length=100)
    status = models.ForeignKey(
        Status,
        verbose_name='Статус',
        on_delete=models.PROTECT,
        related_name='places',
        limit_choices_to={'kind': StatusKind.PLACE},
    )

    class Meta:
        verbose_name = 'Компьютерное место'
        verbose_name_plural = 'Компьютерные места'
        constraints = [
            models.UniqueConstraint(fields=('zone', 'number'), name='uniq_zone_number'),
        ]

    def __str__(self):
        return f'{self.zone} №{self.number}'

    def is_available_for_booking(self) -> bool:
        return (
            self.status.kind == StatusKind.PLACE
            and self.status.code == StatusCodes.PLACE_AVAILABLE
        )


class StatusCodes:
    PLACE_AVAILABLE = 'available'
    PLACE_UNAVAILABLE = 'unavailable'
    BOOKING_NEW = 'new'
    BOOKING_APPROVED = 'approved'
    BOOKING_REJECTED = 'rejected'


class Booking(models.Model):
    place = models.ForeignKey(
        ComputerPlace,
        verbose_name='Место',
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    date = models.DateField('Дата')
    start_time = models.TimeField('Время начала')
    duration = models.PositiveIntegerField('Длительность (мин.)')
    status = models.ForeignKey(
        Status,
        verbose_name='Статус',
        on_delete=models.PROTECT,
        related_name='bookings',
        limit_choices_to={'kind': StatusKind.BOOKING},
    )

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f'{self.place} — {self.date} {self.user}'

    def clean(self):
        super().clean()
        if self.place_id:
            if not self.place.is_available_for_booking():
                raise ValidationError(
                    {'place': 'Это место недоступно для бронирования.'},
                )
