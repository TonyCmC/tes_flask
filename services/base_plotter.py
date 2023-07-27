import abc
import matplotlib.pyplot as plt


class BasePlotter(abc.ABC):
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['axes.titlesize'] = 20
    plt.style.use('dark_background')

    def request_factory(self, api_url, param):
        pass

    @abc.abstractmethod
    def fetch_stock_meta(self, stock_id):
        return NotImplemented

    @abc.abstractmethod
    def fetch_stock_kbars(self, stock_id):
        return NotImplemented

    @abc.abstractmethod
    def data_parser(self, stock):
        return NotImplemented

    @abc.abstractmethod
    def plotter(self, stock):
        return NotImplemented
