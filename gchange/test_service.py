import unittest
from .service import BTCCService

class BTCCServiceTestCase(unittest.TestCase):

    def testAccountInfo(self):
        btcc = BTCCService()
        btcc.get_account_info()

    def testMarketDepth(self):
        btcc = BTCCService()
        btcc.get_market_depth2()