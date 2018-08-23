from rest_framework import serializers
from trader.models import BFEvent

class BFEventSerializer(serializers.ModelSerializer, ):
    class Meta:
        model = BFEvent
        fields =('marids','bfid')
        #'cid','rid1','rid2','pid1','pid2','dt','status')
        #depth = 1
