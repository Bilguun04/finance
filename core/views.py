from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required


def index(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/landing.html")