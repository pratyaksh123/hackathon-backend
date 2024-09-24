from rest_framework import viewsets
from .models import LunchPreference
from .serializers import LunchPreferenceSerializer

class LunchPreferenceViewSet(viewsets.ModelViewSet):
    queryset = LunchPreference.objects.all()
    serializer_class = LunchPreferenceSerializer