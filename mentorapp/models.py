import os
from django.db import models

class Style(models.Model):
    name = models.CharField(max_length=20, default="")

class Mentor(models.Model):
    username = models.CharField(max_length=10, default="unknown")
    profile_image = models.ImageField(upload_to="images/mentor_profiles", default="mentorapp/images/profile_image.png")
    self_introduction = models.CharField(max_length=300, default="")
    style = models.ManyToManyField(Style)

class Coordinate(models.Model):
    name = models.CharField(max_length=20, default="")
    image = models.ImageField(upload_to="images/coordinates")
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)