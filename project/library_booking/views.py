from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView

from .forms import BookingForm, ComputerPlaceForm, StaffBookingStatusForm
from .models import Booking, ComputerPlace, Status, StatusCodes, StatusKind


def _place_list_queryset(request):
    qs = ComputerPlace.objects.select_related('status').order_by('zone', 'number')
    zone = request.GET.get('zone') or ''
    os_name = request.GET.get('os') or ''
    if zone:
        qs = qs.filter(zone=zone)
    if os_name:
        qs = qs.filter(operating_system=os_name)
    return qs, zone, os_name


def _place_list_context(request, booking_form=None):
    places, zone, os_name = _place_list_queryset(request)
    zones = (
        ComputerPlace.objects.order_by('zone')
        .values_list('zone', flat=True)
        .distinct()
    )
    systems = (
        ComputerPlace.objects.order_by('operating_system')
        .values_list('operating_system', flat=True)
        .distinct()
    )
    return {
        'places': places,
        'zones': zones,
        'systems': systems,
        'current_zone': zone,
        'current_os': os_name,
        'booking_form': booking_form if booking_form is not None else BookingForm(),
    }


def place_list(request):
    ctx = _place_list_context(request)
    if request.GET.get('partial') == '1':
        return render(request, 'library_booking/_place_list_inner.html', ctx)
    return render(request, 'library_booking/place_list.html', ctx)


class SiteLoginView(LoginView):
    template_name = 'library_booking/login.html'
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect('library_booking:place_list')


class MyBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'library_booking/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related('place', 'status')
            .order_by('-date', '-start_time')
        )


@login_required
@require_POST
def booking_create(request):
    form = BookingForm(request.POST)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.user = request.user
        booking.status = Status.objects.get(
            code=StatusCodes.BOOKING_NEW,
            kind=StatusKind.BOOKING,
        )
        booking.save()
        messages.success(request, 'Заявка создана.')
        return redirect('library_booking:my_bookings')
    messages.error(request, 'Не удалось создать заявку. Проверьте данные.')
    ctx = _place_list_context(request, booking_form=form)
    return render(request, 'library_booking/place_list.html', ctx)


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy('library_booking:login')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class StaffPlaceAddView(StaffRequiredMixin, CreateView):
    model = ComputerPlace
    form_class = ComputerPlaceForm
    template_name = 'library_booking/staff/place_form.html'
    success_url = reverse_lazy('library_booking:place_list')

    def form_valid(self, form):
        messages.success(self.request, 'Место добавлено.')
        return super().form_valid(form)


class StaffBookingListView(StaffRequiredMixin, ListView):
    model = Booking
    template_name = 'library_booking/staff/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.select_related('place', 'user', 'status').order_by(
            '-date',
            '-start_time',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_form'] = StaffBookingStatusForm()
        return ctx


@require_POST
def staff_booking_status(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden('Недостаточно прав.')
    booking = get_object_or_404(Booking, pk=pk)
    form = StaffBookingStatusForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest('Неверные данные.')
    booking.status = form.cleaned_data['status']
    booking.save(update_fields=['status'])
    messages.success(request, 'Статус заявки обновлён.')
    return redirect('library_booking:staff_booking_list')
