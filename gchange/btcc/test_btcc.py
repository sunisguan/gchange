# -*- coding: utf-8 -*-
import unittest
from ..btcc import btcc_http_client
import btcc_model as bm
import common
import time

class BtccTestCase(unittest.TestCase):

    def testAccountInfo(self):
        btcc = btcc_http_client.BtccHttpClient()

        btcc.get_account_info()
        btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Balance)
        btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Frozen)
        btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Profile)
        btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Loan)

    def testTicker(self):
        for i in range(1, 60):
            btcc = btcc_http_client.BtccHttpClient()
            ticker = bm.Ticker(**btcc.get_ticker()['ticker'])
            common.logger.info(ticker)
            common.logger.info("--------")
            time.sleep(5)




