from django.db import models
from studentapp.models import Student
from mentorapp.models import Mentor

class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE) 
    start_datetime = models.DateTimeField()
    hours = models.DurationField()
