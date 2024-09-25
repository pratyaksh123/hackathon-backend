from django.db.models import Q
from datetime import datetime
from .models import LunchPreference, Match

def calculate_time_overlap(start1, end1, start2, end2):
    latest_start = max(start1, start2)
    earliest_end = min(end1, end2)
    overlap = int((earliest_end - latest_start).seconds / 60)  # overlap in minutes
    if overlap >= 60:
        return 3  # 3 points for 60 or more minutes overlap
    elif overlap >= 30:
        return 2  # 2 points for 30 to 59 minutes overlap
    elif overlap > 0:
        return 1  # 1 point for less than 30 minutes overlap
    return 0

def match_users_for_date(date):
    all_locations = LunchPreference.objects.filter(date=date).values_list('office_location', flat=True).distinct()
    matched_users = set()
    
    for location in all_locations:
        preferences = LunchPreference.objects.filter(date=date, office_location=location)
        # Iterate through each preference to find potential matches
        for pref in preferences:
            potential_matches = preferences.filter(~Q(user=pref.user))
            best_match = None
            highest_score = 0
            
            # Evaluate potential matches for the current preference
            for match in potential_matches:
                if match.user.id in matched_users or pref.user.id in matched_users:
                    continue  # Skip if either user has already been matched

                # Calculate score based on defined criteria
                score = calculate_time_overlap(pref.start_time, pref.end_time, match.start_time, match.end_time)
                if pref.building == match.building:
                    score += 2  # Building match adds 2 points
                shared_topics = pref.topics.all() & match.topics.all()
                score += len(shared_topics)  # Each shared topic adds 1 point

                # Update the best match if this score is higher than the previous highest
                if score > highest_score:
                    best_match = match
                    highest_score = score

            # If a best match was found, create a match entry
            if best_match and highest_score > 0:
                Match.objects.create(user1=pref.user, user2=best_match.user, date=date, score=highest_score)
                matched_users.add(pref.user.id)
                matched_users.add(best_match.user.id)

    # After processing all locations, return the count of new matches created for monitoring or further processing
    return len(matched_users) // 2  # Since each match involves two users
