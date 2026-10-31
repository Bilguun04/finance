from django.shortcuts import render, redirect
from django.http import JsonResponse

def dashboard(request):
    if request.user.is_authenticated:
        return JsonResponse({"message": "Welcome to the portfolio dashboard!"})
    return JsonResponse({"error": "Unauthorized"}, status=401)