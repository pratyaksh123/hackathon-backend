from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import LunchPreferenceSerializer
from .models import LunchPreference, Match
from django.contrib.auth.models import User
from background_task import background
import datetime
from .matcher import match_users_for_date

@api_view(['POST'])
def add_user_lunch_preference(request):
    print("Received data:", request.data)  # Log incoming request data
    serializer = LunchPreferenceSerializer(data=request.data)
    if serializer.is_valid():
        try:
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        print("Validation errors:", serializer.errors)  # Log validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user_lunch_preference(request, user_id):
    try:
        preferences = LunchPreference.objects.filter(user_id=user_id)
        serializer = LunchPreferenceSerializer(preferences, many=True)
        return Response(serializer.data)
    except LunchPreference.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_match(request, user_id, date):
    try:
        user = User.objects.get(pk=user_id)
        match_date = datetime.strptime(date, "%Y-%m-%d").date()
        matches = Match.objects.filter(date=match_date).filter(Q(user1=user) | Q(user2=user))
        
        result = [{
            'user1': match.user1.email,
            'user2': match.user2.email,
            'score': match.score,
            'date': match.date.strftime("%Y-%m-%d")
        } for match in matches]

        return Response(result)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def trigger_matching(request, date):
    try:
        match_date = datetime.strptime(date, "%Y-%m-%d").date()
        match_users_for_date(match_date)
        return Response({'status': 'Matching started for date: ' + date}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_matches_for_date(request, date):
    try:
        match_date = datetime.strptime(date, "%Y-%m-%d").date()
        matches = Match.objects.filter(date=match_date)
        result = [{
            'user1': match.user1.email,
            'user2': match.user2.email,
            'score': match.score,
            'date': match.date
        } for match in matches]
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
