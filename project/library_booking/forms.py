from django import forms
from django.core.exceptions import ValidationError

from .models import Booking, ComputerPlace, Status, StatusKind


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('place', 'date', 'start_time', 'duration')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'duration': forms.NumberInput(attrs={'min': 15, 'step': 15}),
        }

    def clean_place(self):
        place = self.cleaned_data['place']
        if not place.is_available_for_booking():
            raise ValidationError('Это место недоступно для бронирования.')
        return place


class ComputerPlaceForm(forms.ModelForm):
    class Meta:
        model = ComputerPlace
        fields = ('number', 'zone', 'operating_system', 'status')


class StaffBookingStatusForm(forms.Form):
    status = forms.ModelChoiceField(
        label='Статус заявки',
        queryset=Status.objects.none(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = Status.objects.filter(kind=StatusKind.BOOKING).order_by(
            'label',
        )
