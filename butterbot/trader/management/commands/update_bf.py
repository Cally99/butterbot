from trader.tasks import BFCommand
import sys

class Command(BFCommand):
    help = 'Refreshes betfair NI data'

    def handle(self, *args, **options):
        self.betfair_get(False,0)
        sys.exit()