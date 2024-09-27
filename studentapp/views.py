from django.shortcuts import render

# Create your views here.

def home_page_view(request):
    
    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")

        elif user.user_type == "teacher":
            return redirect("manage_schedule")

    else:
        
        return render(request, "studentapp/lp.html")