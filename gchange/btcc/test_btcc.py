# -*- coding: utf-8 -*-
import unittest
from ..btcc import btcc_http_client

class BtccTestCase(unittest.TestCase):

    def testAccountInfo(self):
        btcc = btcc_http_client.BtccHttpClient()

        all = btcc.get_account_info()
        balance = btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Balance)
        frozen = btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Frozen)
        profile = btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Profile)
        loan = btcc.get_account_info(btcc_http_client.BtccHttpClient.AccountParams.Loan)

        print 'all = ', all
        print 'balance = ', balance
        print 'frozen = ', frozen
        print 'profile = ', profile
        print 'loan = ', loan


