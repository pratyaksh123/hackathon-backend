from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from .serializers import LunchPreferenceSerializer, TopicSerializer
from .models import LunchPreference, Match, Topic
from django.contrib.auth.models import User
from background_task import background
from datetime import datetime
from .matcher import match_users_for_date
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()  # Queryset for the viewset
    serializer_class = TopicSerializer  # Serializer for the viewset

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data
    try:
        user = User.objects.create(
            username=data['email'],
            email=data['email'],
            password=make_password(data['password'])
        )
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    try:
        user = request.user  # Get the currently authenticated user
        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_lunch_preference(request):
    print("Received data:", request.data)  # Log incoming request data
    serializer = LunchPreferenceSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = request.data.get('user')  # Fetch the user from the request data
            date = request.data.get('date')  # Fetch the date from the request data

            # Check if a lunch preference already exists for the user and date
            existing_preference = LunchPreference.objects.filter(user=user, date=date).first()

            if existing_preference:
                # Update the existing preference with new data
                serializer = LunchPreferenceSerializer(existing_preference, data=request.data, partial=True)
                if serializer.is_valid():
                    instance = serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:
                # Create a new preference if none exists
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
            'user1': match.user1.id,
            'user2': match.user2.id,
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
        matches_created = match_users_for_date(match_date)
        return Response({'status': f"{matches_created } matches created for date: " + date}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_matches_for_date(request, date):
    try:
        match_date = datetime.strptime(date, "%Y-%m-%d").date()
        matches = Match.objects.filter(date=match_date)
        result = [{
            'user1': match.user1.id,
            'user2': match.user2.id,
            'score': match.score,
            'date': match.date
        } for match in matches]
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_matches_for_date(request, date):
    try:
        # Parse the date string into a datetime object
        match_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # Delete all matches for the given date
        matches_deleted, _ = Match.objects.filter(date=match_date).delete()
        
        if matches_deleted > 0:
            return Response({'status': f'{matches_deleted} matches deleted for date: {date}'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'No matches found for the given date'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)