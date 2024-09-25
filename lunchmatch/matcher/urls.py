from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import TopicViewSet

from django.urls import path
from . import views

# Initialize the router
router = DefaultRouter()
router.register(r'topics', TopicViewSet, basename='topic')

urlpatterns = [
    path('', include(router.urls)),
    path('trigger-matching/<str:date>/', views.trigger_matching, name='trigger-matching'),
    path('matches/<str:date>/', views.get_matches_for_date, name='get-matches-for-date'),
    path('matches/delete/<str:date>/', views.delete_matches_for_date, name='delete-matches-for-date'),
    path('preferences/add/', views.add_user_lunch_preference, name='add-user-lunch-preference'),
    path('preferences/<int:user_id>/', views.get_user_lunch_preference, name='get-user-lunch-preference'),
    path('user/<int:user_id>/matches/<str:date>/', views.get_match, name='get-match'),
]
