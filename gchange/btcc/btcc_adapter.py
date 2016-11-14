# -*- coding: utf-8 -*-

import btcc_http_client
import btcc_model
import common

class BtccHttpAdapter(object):

    def __init__(self):
        self.__hc = btcc_http_client.BtccHttpClient()

    def get_account_profile(self):
        """
        获取用户信息
        :return: UserProfile Model
        """
        ret, status = self.__hc.get_account_info(acount_type=btcc_http_client.BtccHttpClient.AccountParams.Profile)
        if status:
            return btcc_model.UserProfile(**ret)
        else:
            return None

    def __get_balance(self, icon):
        """
        获取指定货币的账户余额
        :param icon: common.CoinSymbol, BTC/LTC/CNY
        :return: btcc_model.Balance
        """
        ret, status = self.__hc.get_account_info(acount_type=btcc_http_client.BtccHttpClient.AccountParams.Balance)
        if status and icon in common.CoinSymbol.COIN_SYMBOLS:
            return btcc_model.Balance(**ret[icon])
        else:
            return None

    def get_balance_btc(self):
        """
        获取BTC账户余额
        :return: btcc_model.Balance
        """
        return self.__get_balance(common.CoinSymbol.BTC)



