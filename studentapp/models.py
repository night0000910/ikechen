from django.db import models

class Student(models.Model):
    username = models.TextField(default="")
    profile_image = models.ImageField(upload_to="", default="images/profile_image.png")