from django.contrib.auth.models import User
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    text_resume = models.TextField()

    def __str__(self):
        return self.user.username


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    match_score = models.FloatField()

    def __str__(self):
        return f"{self.title} at {self.company.name}"
