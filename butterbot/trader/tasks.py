from __future__ import absolute_import , unicode_literals

import django

django.setup()

from betfairlightweight.filters import market_filter , time_range , price_data , place_instruction , price_projection
from trader.client import get_betfair_client
from django.core.management.base import BaseCommand , CommandError
from trader.models import BFChamp , BFPlayer , BFEvent , BFOdds
from trader.models import ALog
from django.utils import timezone
from django.conf import settings


class BFCommand(BaseCommand):
    is_debug = True
    sport = {'Tennis': 2}

    def betfair_get(self , is_ip , counter , sport='Tennis'):
        start = timezone.now()
        ip = 'ip' if is_ip else 'ni'

        trading = get_betfair_client()

        trading.login()
        trading.keep_alive()
        tennis_event_type = self.sport[sport]
        markets = trading.betting.list_market_catalogue(
            market_filter(event_type_ids=[tennis_event_type] , market_type_codes=["MATCH_ODDS"] , in_play_only=is_ip) ,
            market_projection=[
                "MARKET_DESCRIPTION" ,
                "RUNNER_DESCRIPTION" ,
                "EVENT" ,
                "EVENT_TYPE" ,
                "COMPETITION" ,
                "RUNNER_METADATA" ,
                "MARKET_START_TIME" ,
            ] ,
            max_results=100)

        mids = [m.market_id for m in markets]
        mids_portions = [mids[x:x + 40] for x in range(0 , len(mids) , 40)]
        #print(mids[0])
        for mp in mids_portions:
            (','.join(mp))
            books = trading.betting.list_market_book(
                market_ids=mp ,
                price_projection=price_projection(
                    price_data(

                        ex_best_offers=True ,
                    )
                ) ,
                lightweight=False)

            for b in books:

                m = next((x for x in markets if x.market_id == b.market_id) , None)

                if m.competition == None: continue

                bfcid = m.competition.id
                marids = m.market_id
                print(marids)
                champname = m.competition.name
                country = m.event.country_code
                event_id = m.event.id
                ds = timezone.make_aware(m.event.open_date)
                p1 = m.runners[0].runner_name

                if (p1 == None or '/' in p1):
                    continue

                rid1 = m.runners[0].selection_id
                p2 = m.runners[1].runner_name
                rid2 = m.runners[1].selection_id
                event , created = BFEvent.objects.get_or_create(bfid=event_id)

                if (created):
                    champ = self.save_champ(bfcid , champname , tennis_event_type , country)
                    player1 = self.save_player(p1)
                    player2 = self.save_player(p2)
                    event.cid = champ
                    event.marids = marids
                    event.rid1 = rid1
                    event.rid2 = rid2
                    event.pid1 = player1
                    event.pid2 = player2
                    event.dt = ds
                    event.status = 1 if is_ip else 0
                    event.save()
                p1b1_odds=b.runners[0].ex.available_to_back[0].price if len(b.runners[0].ex.available_to_back)>0 else 0
                p1b1_size=b.runners[0].ex.available_to_back[0].size if len(b.runners[0].ex.available_to_back)>0 else 0
                p1l1_odds=b.runners[0].ex.available_to_lay[0].price if len(b.runners[0].ex.available_to_lay)>0 else 0
                p1l1_size=b.runners[0].ex.available_to_lay[0].size if len(b.runners[0].ex.available_to_lay)>0 else 0
                p2b1_odds=b.runners[1].ex.available_to_back[0].price if len(b.runners[1].ex.available_to_back)>0 else 0
                p2b1_size=b.runners[1].ex.available_to_back[0].size if len(b.runners[1].ex.available_to_back)>0 else 0
                p2l1_odds=b.runners[1].ex.available_to_lay[0].price if len(b.runners[1].ex.available_to_lay)>0 else 0
                p2l1_size=b.runners[1].ex.available_to_lay[0].size if len(b.runners[1].ex.available_to_lay)>0 else 0

                try:
                    odds= BFOdds.objects.filter(eid=event).latest('dtc')
                    if(odds.b1odds!=p1b1_odds or odds.b2odds!=p2b1_odds or odds.l1odds!=p1l1_odds or odds.l2odds!=p2l1_odds):
                        self.save_odds(event,p1b1_odds,p2b1_odds,p1l1_odds,p2l1_odds,p1b1_size,p2b1_size,p1l1_size,p2l1_size,is_ip)
                        if (self.is_debug):
                            self.stdout.write('evid[%s], mid[%s] %s %s - %s in %s: %s/%s\n' % (event_id,b.market_id, ds,p1.replace('\\',''),p2.replace('\\',''),country,b.total_matched,b.total_available), ending='')
                            self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid1,p1.replace('\\',''), p1b1_size,p1b1_odds,p1l1_size,p1l1_odds), ending='')
                            self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid2,p2.replace('\\',''), p2b1_size,p2b1_odds,p2l1_size,p2l1_odds), ending='')
                except:
                    self.save_odds(event,p1b1_odds,p2b1_odds,p1l1_odds,p2l1_odds,p1b1_size,p2b1_size,p1l1_size,p2l1_size,is_ip)
                    if (self.is_debug):
                        self.stdout.write('evid[%s], mid[%s] %s %s - %s in %s: %s/%s\n' % (event_id,b.market_id, ds,p1.replace('\\',''),p2.replace('\\',''),country,b.total_matched,b.total_available), ending='')
                        self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid1,p1.replace('\\',''), p1b1_size,p1b1_odds,p1l1_size,p1l1_odds), ending='')
                        self.stdout.write('[%s]%s:%s@%s\t|%s@%s\n' % (rid2,p2.replace('\\',''), p2b1_size,p2b1_odds,p2l1_size,p2l1_odds), ending='')
        end=timezone.now()
        log=ALog()
        log.name='update_bf_%s_%s' % (sport,ip)
        log.dts=start
        log.counter=counter
        log.duration=(end-start).total_seconds()
        log.save()
        if (self.is_debug):
            self.stdout.write('total execution is %s seconds\n' %(end-start), ending='')





    def save_champ(self , bfcid , name , sport , country_code):
        champ , created = BFChamp.objects.get_or_create(bfid=bfcid)
        if created:
            if settings.DEBUG:
                self.stdout.write('created a new champ, id=%s\n' % champ.id , ending='')
                champ.sport = sport
                champ.name = name
                champ.country_code = country_code
                champ.save()
        return champ

    def save_player(self , name):
        player , created = BFPlayer.objects.get_or_create(name=name)
        return player


    def save_odds(self , eid , p1b1_odds , p2b1_odds , p1l1_odds , p2l1_odds , p1b1_size , p2b1_size , p1l1_size ,
                  p2l1_size , is_ip):
        dtc = timezone.now()
        odds = BFOdds()
        odds.eid = eid
        odds.b1odds = p1b1_odds
        odds.b2odds = p2b1_odds
        odds.l1odds = p1l1_odds
        odds.l2odds = p2l1_odds
        odds.b1size = p1b1_size
        odds.b2size = p2b1_size
        odds.l1size = p1l1_size
        odds.l2size = p2l1_size
        odds.ip = is_ip
        odds.dtc = dtc
        odds.save()
        eid.dtc = dtc
        eid.save()
