from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LunchPreferenceViewSet

router = DefaultRouter()
router.register(r'preferences', LunchPreferenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
