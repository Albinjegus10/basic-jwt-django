from django.shortcuts import render

from django.http import HttpResponse


def hello2(request):
    return HttpResponse("online class")
