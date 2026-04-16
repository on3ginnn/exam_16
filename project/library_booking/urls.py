from django.urls import path

from . import views

app_name = 'library_booking'

urlpatterns = [
    path('', views.place_list, name='place_list'),
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('bookings/my/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('staff/places/add/', views.StaffPlaceAddView.as_view(), name='staff_place_add'),
    path('staff/bookings/', views.StaffBookingListView.as_view(), name='staff_booking_list'),
    path(
        'staff/bookings/<int:pk>/status/',
        views.staff_booking_status,
        name='staff_booking_status',
    ),
]
