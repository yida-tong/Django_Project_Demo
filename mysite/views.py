from django.shortcuts import render
from django.http import Http404, HttpResponse


def index(request):
    context_dict = {}
    return HttpResponse('sup')