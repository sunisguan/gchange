# -*- coding: utf-8 -*-
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from pyalgotrade import plotter

import common
import abc

CONFIG = {
    'BACKTESTING': True,
    'DURATION': 60*60,
    'SMA_PARAS': [30, 60],
    'START_CAPTIAL': 1000.00,
    'POSITION_SIZE': 0.001,
    'SMA_PERIOD': 40
}


class StrategyHelper(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_position(self):
        raise NotImplemented()

    @abc.abstractmethod
    def get_sma(self):
        raise NotImplemented()


class StrategyRun(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(StrategyRun, self).__init__()
        self.__strategy = None

    @abc.abstractmethod
    def config_live(self):
        raise NotImplemented()

    @abc.abstractmethod
    def config_backtesting(self):
        raise NotImplemented()

    def run(self):
        if CONFIG['BACKTESTING']:
            self.__strategy = self.config_backtesting()
            StrategyRun.__run_backtesting(self.__strategy)
        else:
            self.__strategy = self.config_live()
            StrategyRun.__run_live(self.__strategy)

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
        #plt.getOrCreateSubplot('position').addDataSeries('position', strategy.get_position())
        for k, v in strategy.get_sma().iteritems():
            plt.getInstrumentSubplot('indicator').addDataSeries(k, v)

        strategy.run()

        print '[收益率: ', strategy.getBroker().getEquity() / CONFIG['START_CAPTIAL'], ']'
        print '[STRATEGY FINISH]'

        # 夏普率
        sharp = sharpeRatioAnalyzer.getSharpeRatio(0.05)
        print '[夏普率: ', sharp, ']'

        # 最大回撤
        maxdd = drawDownAnalyzer.getMaxDrawDown()
        print '[最大回撤: ', maxdd, ']'

        # 收益率
        return_ = retAnalyzer.getCumulativeReturns()[-1]
        print '[收益率: ', return_, ']'

        # 收益曲线
        return_list = []
        for item in retAnalyzer.getCumulativeReturns():
            return_list.append(item)

        plt.plot()