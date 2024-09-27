from django.db import models

class Style(models.Model):
    name = models.CharField(max_length=20, default="")

class Mentor(models.Model):
    username = models.CharField(max_length=10, default="unknown")
    profile_image = models.ImageField(upload_to="", default="images/profile_image.png")
    self_introduction = models.CharField(max_length=300, default="")
    style = models.ManyToManyField(Style)
