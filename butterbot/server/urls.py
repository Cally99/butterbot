from django.urls import path, include
from server.views import BFEventView
urlpatterns =[
    path('server/', BFEventView.as_view(), name="songs-all")

]