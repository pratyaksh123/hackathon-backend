from rest_framework import serializers
from .models import LunchPreference, Topic, Match
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']

class LunchPreferenceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Use the default User model
    topics = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True)

    class Meta:
        model = LunchPreference
        fields = ['id', 'user', 'office_location', 'building', 'date', 'start_time', 'end_time', 'topics']

    def create(self, validated_data):
        # Extract the topics data
        topics_data = validated_data.pop('topics')

        # Create the LunchPreference instance
        lunch_preference = LunchPreference.objects.create(**validated_data)

        # Set the many-to-many relationship for topics
        lunch_preference.topics.set(topics_data)

        return lunch_preference

class MatchSerializer(serializers.ModelSerializer):
    user1_email = serializers.EmailField(source='user1.email')
    user2_email = serializers.EmailField(source='user2.email')
    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Match
        fields = ['user1_email', 'user2_email', 'score', 'date']