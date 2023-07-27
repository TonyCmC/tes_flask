import json
import logging
import re
import unittest

import numpy as np
import pandas as pd
import pytz
import requests

import config
from services.fugle_plotter_service import FuglePlotterService
from services.redis_service import RedisService
from utils.logger import Logger
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num
from mplfinance.original_flavor import candlestick2_ohlc
from datetime import datetime, timedelta


class TestFugle(unittest.TestCase):
    def setUp(self) -> None:
        self.fps = FuglePlotterService()

    def tearDown(self) -> None:
        pass

    def test_empty(self):
        stock_id = '2330'
        self.fps.data_parser(stock_id)

    def test_fetch_stock_meta(self):
        stock_id = '2330'
        self.fps.plotter(stock_id)

    def test_redis_meta(self):
        rs = RedisService()
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2498')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2006')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))
        rs.redis.hset('metas', '2330', json.dumps(self.fps.fetch_stock_meta('2002')))

    def test_logger(self):
        import pandas as pd
        import matplotlib.pyplot as plt

        # Create an empty DataFrame with a fixed datetime index from 9:00 to 13:30 with one-minute intervals
        market_open_time = pd.Timestamp("2023-07-21T09:00:00.000+08:00")
        market_close_time = pd.Timestamp("2023-07-21T13:24:00.000+08:00")
        datetime_index = pd.date_range(start=market_open_time, end=market_close_time, freq='1T')
        empty_df = pd.DataFrame(index=datetime_index)

        # Add the market reopening time at 13:30
        market_reopen_time = pd.Timestamp("2023-07-21T13:30:00.000+08:00")
        datetime_index = datetime_index.union(pd.DatetimeIndex([market_reopen_time]))

        # Reindex the empty DataFrame with the updated datetime_index
        empty_df = empty_df.reindex(datetime_index)

        # Now, you can update the DataFrame with your stock data every minute

        # For example, let's say you receive the stock data as a dictionary:
        data = {
            "date": "2023-07-21T09:01:00.000+08:00",
            "open": 561,
            "high": 563,
            "low": 560,
            "close": 561,
            "volume": 3480,
            "average": 561.12
        }

        # Convert the "date" string to a pandas.Timestamp object
        data["date"] = pd.Timestamp(data["date"])

        # Set the "date" column as the DataFrame's index
        data_df = pd.DataFrame(data, index=[data["date"]])

        # Merge the new data with the empty DataFrame
        updated_df = pd.merge(empty_df, data_df, how="left", left_index=True, right_index=True)
        print(empty_df)
        print(data_df)
        print(updated_df)
        # Fill NaN values with the last available data (forward fill)
        updated_df.fillna(method="ffill", inplace=True)
        print(updated_df.index)

        # Plot the candlestick chart or any other visualization
        # For example, to plot a line chart of "close" prices:
        plt.plot(updated_df.index, updated_df["close"], label="Close Price")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.title("Stock Price Chart")
        plt.legend()
        plt.show()

    def test_sort(self):
        with open('data/fake_chart.json', 'r', encoding='utf-8') as f:
            charts = f.read()
        charts = json.loads(charts)
        df = pd.DataFrame.from_records(charts['data'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        print(df)
        fig, ax = plt.subplots()

        # Convert the date strings to numerical format for candlestick_ohlc
        ohlc_data = df.reset_index()
        ohlc_data['date'] = ohlc_data['date'].apply(date2num)
        ohlc_data = ohlc_data[['date', 'open', 'high', 'low', 'close']]

        candlestick2_ohlc(ax,
                          ohlc_data['open'],
                          ohlc_data['high'],
                          ohlc_data['low'],
                          ohlc_data['close'], width=0.6,
                          colorup='g', colordown='r')

        # Optionally, you can add gridlines and axis labels for better visualization
        ax.grid(True)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Format the dates on the x-axis
        date_formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(date_formatter)
        plt.xticks(rotation=45)

        plt.title('Candlestick Chart')
        plt.tight_layout()

        plt.show()
