import pandas as pd
from django.shortcuts import render, redirect
from rest_framework import generics
from trader.models import BFEvent
from .serializers import BFEventSerializer
from statistics import mean
from django.core.cache import cache

def index(request):

    return render(request, 'bot/index.html')



class BFEventView(generics.ListAPIView):
    queryset = BFEvent.objects.all()
    serializer_class = BFEventSerializer

