import logging
from datetime import datetime
from django.db.models import Q
from .models import LunchPreference, Match

# Set up a logger
logger = logging.getLogger(__name__)

def calculate_time_overlap(start1, end1, start2, end2):
    try:
        # Combine time objects with a reference date
        reference_date = datetime.today()
        start1_datetime = datetime.combine(reference_date, start1)
        end1_datetime = datetime.combine(reference_date, end1)
        start2_datetime = datetime.combine(reference_date, start2)
        end2_datetime = datetime.combine(reference_date, end2)

        latest_start = max(start1_datetime, start2_datetime)
        earliest_end = min(end1_datetime, end2_datetime)

        # Now subtract the datetime objects
        overlap = (earliest_end - latest_start).total_seconds() / 60  # Overlap in minutes

        if overlap >= 60:
            return 3  # 3 points for 60 or more minutes overlap
        elif overlap >= 30:
            return 2  # 2 points for 30 to 59 minutes overlap
        elif overlap > 0:
            return 1  # 1 point for less than 30 minutes overlap
        return 0
    except Exception as e:
        logger.error(f"Error calculating time overlap: {e}")
        return 0  # If there's an error, assume no overlap

def match_users_for_date(date):
    try:
        # Check if any matches already exist for the given date
        existing_matches = Match.objects.filter(date=date).exists()
        if existing_matches:
            logger.info(f"Matches have already been created for date {date}. Skipping.")
            return 0  # Return 0 to indicate no new matches were created

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
    except Exception as e:
        logger.error(f"Error in matching users for date {date}: {e}")
        return 0  # Return 0 if there's an error
