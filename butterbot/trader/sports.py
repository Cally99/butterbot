
from trader.client import get_betfair_client, ET_TENNIS
from betfairlightweight.filters import market_filter , time_range , price_data , place_instruction , price_projection

def list_market_catalogue():
    trading = get_betfair_client()

    mfilter = market_filter(
        event_type_ids=[ET_TENNIS],
        market_start_time=time_range(

        )
    )
    m= trading.betting.list_competitions(mfilter())
    print(m)
    res = trading.betting.list_market_catalogue(
        mfilter,
        market_projection=[
            'EVENT',
            'MARKET_START_TIME',
            'RUNNER_METADATA',
            'COMPETITION',
        ],
        sort='FIRST_TO_START',
        max_results=100,
        lightweight=True)
'''
    comp = trading.betting.list_competitions(market_filter(res,))
    print(comp)
'''


list_market_catalogue()
'''    
    if not len(res):
        logger.error('Market catalogue listing is empty')
        trading.session_token = None
        raise self.retry(countdown=5, max_retries=12)

    for cat in res:
        if 'venue' not in cat['event']:
            logger.error(f'No event venue in {cat}')
            continue
        try:
            event = parse_event(cat['event'])
            market = parse_market(event, cat)
            runners = parse_runners(market, cat['runners'])
        except:
            logger.warning(cat)
            raise
    logger.warning(f'BETFAIR: Scraped {len(res)} from market catalogue')
'''