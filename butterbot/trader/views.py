from django.shortcuts import render
from django.views import View
from trader.models import ALog
from trader.models import BFChamp , BFEvent , BFPlayer , BFOdds, BFEventTable
from server.models import MChamp , MEvent , PlayerSetStats
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime , timedelta
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse


def simple_list_event(request):
    queryset = BFEvent.objects.all()
    table = BFEventTable(queryset)
    return render(request, 'simple_list_event.html', {'table': table})