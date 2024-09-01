from django.urls import include, path

from room_booking import views


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('room-booking/', views.RoomBooking.as_view(), name='room-booking'),
    path('room/<str:room_name>/schedule/', views.RoomSchedule.as_view(), name='room-schedule'),
    path('room-report/', views.BookingReportList.as_view(), name='room-report-list'),
    path('room-report/<str:room_name>/', views.BookingReportRetieve.as_view(), name='room-report-retrieve')
]
