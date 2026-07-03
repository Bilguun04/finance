from django.http import HttpResponse


def home(request):
    return HttpResponse("<h1>Django is running in Docker.</h1>")