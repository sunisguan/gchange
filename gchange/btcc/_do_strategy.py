# -*- coding: utf-8 -*-
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from pyalgotrade import plotter

import abc

CONFIG = {
    'BACKTESTING': True,
    'DURATION': 60*2,
    'SMA_PARAS': [30, 60],
    'START_CAPTIAL': 1000.00,
    'POSITION_SIZE': 0.001,
    'SMA_PERIOD': 20
}


class StarategyRun(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def config_live(self):
        raise NotImplemented()

    @abc.abstractmethod
    def config_backtesting(self):
        raise NotImplemented()

    def run(self):
        if CONFIG['BACKTESTING']:
            StarategyRun.__run_backtesting(self.config_backtesting())
        else:
            StarategyRun.__run_live(self.config_live())

    @classmethod
    def __run_live(cls, strategy):
        strategy.run()
        print '[STRATEGY FINISH]'

    @classmethod
    def __run_backtesting(cls, strategy):

        retAnalyzer = returns.Returns()

        strategy.attachAnalyzer(retAnalyzer)

        sharpeRatioAnalyzer = sharpe.SharpeRatio()

        strategy.attachAnalyzer(sharpeRatioAnalyzer)

        drawDownAnalyzer = drawdown.DrawDown()

        strategy.attachAnalyzer(drawDownAnalyzer)

        tradesAnalyzer = trades.Trades()

        strategy.attachAnalyzer(tradesAnalyzer)

        plt = plotter.StrategyPlotter(strategy, True, True, True)

        strategy.run()

        print '[收益率: ', strategy.getBroker().getEquity() / CONFIG['START_CAPTIAL'], ']'
        print '[STRATEGY FINISH]'

        # 夏普率
        sharp = sharpeRatioAnalyzer.getSharpeRatio(0.05)
        # 最大回撤
        maxdd = drawDownAnalyzer.getMaxDrawDown()
        # 收益率
        return_ = retAnalyzer.getCumulativeReturns()[-1]
        print sharp, maxdd, return_

        # 收益曲线
        return_list = []
        for item in retAnalyzer.getCumulativeReturns():
            return_list.append(item)

        plt.plot()