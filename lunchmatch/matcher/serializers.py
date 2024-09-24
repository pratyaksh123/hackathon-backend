from rest_framework import serializers
from .models import LunchPreference, User, Topic

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']

class LunchPreferenceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = LunchPreference
        fields = ['id', 'user', 'office_location', 'date', 'start_time', 'end_time', 'topics']
