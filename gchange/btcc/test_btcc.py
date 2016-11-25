# -*- coding: utf-8 -*-
import unittest
from ..btcc.btcc_http_client import BtccHttpClient
from .btcc_exchange import BtccExchange, BtccWebsocketClient
import btcc_model as bm
import common
import time

class BtccTestCase(unittest.TestCase):

    def testWebSocket(self):
        btcc = BtccExchange(duration=10)
        btcc.start_websocket_client()

    def socket_handler(self, *args):
        """
        测试 exchange 的订阅回调
        :return:
        """
        common.logger.debug('receive socket data, args = %s' % args[0])

    def testBtccExchange(self):
        btcc = BtccExchange(duration=10)
        btcc.start_websocket_client()
        btcc.subscribe_event(BtccWebsocketClient.Event.ON_TICKER, self.socket_handler)


    def testAccountInfo(self):
        btcc = BtccHttpClient()

        btcc.get_account_info()
        btcc.get_account_info(BtccHttpClient.AccountParams.Balance)
        btcc.get_account_info(BtccHttpClient.AccountParams.Frozen)
        btcc.get_account_info(BtccHttpClient.AccountParams.Profile)
        btcc.get_account_info(BtccHttpClient.AccountParams.Loan)

    def testTicker(self):
        btcc = BtccHttpClient()
        bm.Ticker(**btcc.get_ticker()['ticker'])




