from datetime import datetime, timedelta

import pandas as pd
import pytz
from matplotlib import pyplot as plt

from services.base_plotter import BasePlotter
from fugle_marketdata import RestClient

from config import *
from services.redis_service import RedisService
from utils.logger import Logger


class FuglePlotterService(BasePlotter):
    def __init__(self):
        self.client = RestClient(api_key=FUGLE_TOKEN)
        self.stock = self.client.stock
        self.last_closed_date = datetime.today().strftime('%Y-%m-%d')
        self.rds = RedisService()
        self.logger = Logger('fugle').logger
        self.logger.info('fugle start')

    def fetch_all_tickers(self) -> list:
        markets = [['EQUITY', 'TWSE'], ['EQUITY', 'TPEx'], ['INDEX', 'TWSE'], ['INDEX', 'TPEx']]
        stocks = []
        try:
            for market_type, exchange in markets:
                stocks += self.stock.intraday.tickers(type=market_type, exchange=exchange, isNormal=True)['data']
            return stocks
        except Exception:
            raise ConnectionError('Fail to connect to Fugle service')

    def fetch_stock_meta(self, stock_id: str) -> dict:
        today = datetime.today().strftime('%Y-%m-%d')
        ticker = self.rds.get_metas('2330')

        if ticker is None or ticker['date'] != today:
            try:
                ticker = self.stock.intraday.ticker(symbol=stock_id)
                self.rds.update_metas(ticker)
                self.logger.info(f'call /ticker, response={ticker}')
            except Exception:
                raise ConnectionError('Fail to connect to Fugle service')
        return ticker

    def fetch_stock_kbars(self, stock_id):
        try:
            candles = self.stock.intraday.candles(symbol=stock_id)
            self.logger.info(f'call /candles, response={candles}')
        except Exception:
            raise ConnectionError('Fail to connect to Fugle service')
        return candles

    def generate_empty_dates(self, candles):
        self.last_closed_date = candles['date']
        market_open_time = pd.Timestamp(f"{self.last_closed_date}T09:01:00+08:00")
        market_close_time = pd.Timestamp(f"{self.last_closed_date}T09:24:00+08:00")
        datetime_index = pd.date_range(start=market_open_time, end=market_close_time, freq='1T')
        empty_df = pd.DataFrame(index=datetime_index)

        market_reopen_time = pd.Timestamp(f"{self.last_closed_date}T13:30:00+08:00")
        datetime_index = datetime_index.union(pd.DatetimeIndex([market_reopen_time]))
        empty_df = empty_df.reindex(datetime_index)

        return empty_df

    def data_parser(self, stock_id):
        candles = self.fetch_stock_kbars(stock_id)
        empty_dates = self.generate_empty_dates(candles)
        empty_row = [0] * len(empty_dates)
        candles = pd.DataFrame.from_records(candles['data'])
        candles = candles.rename({'date': 'time'}, axis=1)
        candles.set_index('time', inplace=True)

        print(empty_dates)
        print(candles)
        # Merge the new data with the empty DataFrame
        updated_df = pd.merge(empty_dates, candles, how="left", on='time')

        # Fill NaN values with the last available data (forward fill)
        updated_df.fillna(method="ffill", inplace=True)
        return updated_df

    def plotter(self, stock_id):
        updated_df = self.data_parser(stock_id)
        print(updated_df)
        plt.plot(updated_df.index, updated_df["close"], label="Close Price")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.title("Stock Price Chart")
        plt.legend()
        plt.show()
