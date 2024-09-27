from django.shortcuts import render
from mentorapp.models import Mentor

def view_lp(request):
    return render(request, "studentapp/lp.html")

def view_list_mentors(request):
    mentors = Mentor.objects.all()
    return render(request, 
                  "studentapp/list_mentors.html",
                  {'mentors' : mentors})
