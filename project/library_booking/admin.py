from django.contrib import admin

from .models import Booking, ComputerPlace, Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'label', 'kind')
    list_filter = ('kind',)


@admin.register(ComputerPlace)
class ComputerPlaceAdmin(admin.ModelAdmin):
    list_display = ('number', 'zone', 'operating_system', 'status')
    list_filter = ('zone', 'operating_system', 'status')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('place', 'user', 'date', 'start_time', 'duration', 'status')
    list_filter = ('status', 'date')
