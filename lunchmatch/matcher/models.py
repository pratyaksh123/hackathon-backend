from django.contrib.auth.models import User
from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class LunchPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Use Django's default User model
    office_location = models.CharField(max_length=20)
    building = models.CharField(max_length=10)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topics = models.ManyToManyField(Topic)

    def __str__(self):
        return f"{self.user.email} - {self.date}"

class Match(models.Model):
    user1 = models.ForeignKey(User, related_name='matches_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='matches_as_user2', on_delete=models.CASCADE)
    date = models.DateField()
    score = models.IntegerField()

    def __str__(self):
        return f"{self.user1.email} - {self.user2.email} - {self.date} - Score: {self.score}"
