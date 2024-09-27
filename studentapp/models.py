from django.db import models

class Student(models.Model):
    username = models.CharField(max_length=10, default="unknown")
    profile_image = models.ImageField(upload_to="images/student_profiles", default="images/profile_image.png")