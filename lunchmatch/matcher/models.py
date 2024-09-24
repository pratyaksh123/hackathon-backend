from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    # Add additional fields as necessary


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class LunchPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    office_location = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topics = models.ManyToManyField(Topic)  # Allows multiple topics selection

    def __str__(self):
        return f"{self.user.username} - {self.date}"