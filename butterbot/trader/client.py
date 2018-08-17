import datetime
import json
import logging
import requests
from betfairlightweight import APIClient
from betfairlightweight.endpoints.baseendpoint import BaseEndpoint
from betfairlightweight.filters import market_filter
from betfairlightweight.filters import price_projection, price_data, time_range
from django.utils import timezone
import redis
from key.secrets import APP_KEY_DEV, APP_URL_LOGIN, USERNAME, PASSWORD, APP_CERTS_DIR, CERT, KEY
import inspect
BaseEndpoint.connect_timeout = 10
BaseEndpoint.read_timeout = 30

trading = APIClient(USERNAME, PASSWORD, APP_KEY_DEV, APP_CERTS_DIR)
ET_SOCCER = 1
ET_TENNIS = 2
ET_GOLF = 3
ET_CRICKET = 4
ET_RUGBY_UNION = 5
ET_BOXING = 6
ET_HORSE_RACING = 7
ET_MOTOR_SPORT = 8
ET_SPECIAL_BETS = 10
ET_CYCLING = 11
ET_GREYHOUND_RACING = 4339

redis_client = redis.Redis()
log = logging.getLogger(__name__)

def get_betfair_client():
    if not trading.session_token:
        trading.login()
    return trading




def custom_login():
    """login to betfair"""

    data = {
        'username': USERNAME,
        'password': PASSWORD,
    }
    res = requests.post(APP_URL_LOGIN, data,cert=(CERT, KEY),
                        headers={'X-Application': APP_KEY_DEV,'Content-Type': 'application/x-www-form-urlencoded'},
                        )

    res.raise_for_status()
    res = res.json()
    print(res)




def login():
    """login to betfair"""
    res = trading.login()
    print(res.login_status)
    print(res.session_token)

def list_event_types():
    """list event types"""
    login()
    res = trading.betting.list_event_types()
    for item in res:
        print(f'market count: {item.market_count}')
        print(f'event: [{item.event_type.id}] {item.event_type.name}')

#list_event_types()
def list_market_types():
    """market types"""
    login()
    res = trading.betting.list_market_types()
    for item in res:
        print(f'market count: {item.market_count}')
        print(f'market: {item.market_type}')
#list_market_types()

def list_venues():
    login()
    mfilter = market_filter(
        event_type_ids=[ET_GREYHOUND_RACING, ET_HORSE_RACING],
    )
    res = trading.betting.list_venues(mfilter)
    res.sort(key=lambda x: x.market_count, reverse=True)
    for item in res:
        print(f'venue: {item.market_count}: {item.venue}')
#list_venues()

def list_events():
    """list greyhound events"""
    trading = get_betfair_client()
    mfilter = market_filter(
        event_type_ids=[ET_TENNIS],
    )
    res = trading.betting.list_events(mfilter)
    print(f'res length {len(res)}')
    res.sort(key=lambda x: x.event.open_date)
    for item in res:
        print(f'market count: {item.market_count}')
        print(f'event: [{item.event.id}] {item.event.name}')
        print(f'open: {item.event.open_date} {item.event.venue}')
        #print(f'loc: {item.event.country_code} {item.event.time_zone}')

def list_market_cat(event_id=None, market_id=None):
    trading = get_betfair_client()
    time_ago = timezone.now() - datetime.timedelta(minutes=10)
    time_fwd = timezone.now() + datetime.timedelta(minutes=30)
    mfilter = market_filter(
        event_type_ids=[ET_TENNIS],
       # market_start_time=time_range(
        #    from_=time_ago.strftime('%Y-%m-%dT%H:%I:%S.000Z'),
        #    to=time_fwd.strftime('%Y-%m-%dT%H:%I:%S.000Z')

    )
    res = trading.betting.list_market_catalogue(
        mfilter,
        market_projection=[
            'EVENT',
            'MARKET_START_TIME',



        ],
        sort='FIRST_TO_START',
        max_results=500,
        lightweight=True)
    print(json.dumps(res, indent=4, default=str, sort_keys=True))
    print(len(res))
    if event_id:
        mfilter = market_filter(event_ids=[event_id])
    elif market_id:
        mfilter = market_filter(market_ids=[market_id])
    res = trading.betting.list_market_catalogue(mfilter)
    cat = res[0]
    print(f'runners: {len(cat.runners)}')
    for runner in cat.runners:
        print(f'{runner.name}')


def list_market_book(market_id):
    trading = get_betfair_client()
    res = trading.betting.list_market_book(
        market_ids=[market_id],
        price_projection=price_projection(
            price_data(
                sp_available=False,
                sp_traded=False,
                ex_best_offers=True,
                ex_all_offers=False,
                ex_traded=True,
            )
        ),
        order_projection='ALL',
        match_projection='ROLLED_UP_BY_PRICE',
        lightweight=True)
    print(f'res length {len(res)}')
    print(json.dumps(res, indent=3))


