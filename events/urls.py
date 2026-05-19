from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('create/', views.event_create, name='event_create'),
    path('<int:pk>/update/', views.event_update, name='event_update'),
    path('<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('<int:pk>/review/add/', views.add_review, name='add_review'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
    path('<int:pk>/register/', views.register_for_event, name='register_for_event'),
    path('<int:pk>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('<int:pk>/ticket/', views.generate_pdf_ticket, name='generate_pdf_ticket'),
]