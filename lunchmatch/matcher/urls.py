from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('trigger-matching/<str:date>/', views.trigger_matching, name='trigger-matching'),
    path('matches/<str:date>/', views.get_matches_for_date, name='get-matches-for-date'),
    path('preferences/add/', views.add_user_lunch_preference, name='add-user-lunch-preference'),
    path('preferences/<int:user_id>/', views.get_user_lunch_preference, name='get-user-lunch-preference'),
    path('user/<int:user_id>/matches/<str:date>/', views.get_match, name='get-match'),
]
