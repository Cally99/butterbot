from django.contrib import admin
from .models import BFEvent, BFOdds, BFPlayer,BFChamp,ALog



# Register your models here.
#admin.site.register(Tennis)

admin.site.register(BFOdds)
admin.site.register(BFEvent)
admin.site.register(BFPlayer)
admin.site.register(BFChamp)
admin.site.register(ALog)