from django.shortcuts import render


def view_lp(request):
    return render(request, "studentapp/lp.html")
