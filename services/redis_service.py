import json
import re

import pandas as pd
import redis
from config import *
from utils.logger import Logger


class RedisService:
    def __init__(self):
        self.logger = Logger('redis').logger
        self.redis = redis.Redis(host='localhost',
                                 port=REDIS_PORT,
                                 decode_responses=True)

    def clear_redis(self):
        self.redis.flushdb()

    def get_redis(self):
        return self.redis

    def switch_db(self, db_index: int):
        self.redis.select(db_index)

    def update_tickers(self, tickers: list):
        self.switch_db(1)

        if len(tickers) != 0:
            self.logger.info('ticker is empty, use local ticker instead.')
            tickers = pd.read_csv(f'{ROOT_DIR}/data/stocks.csv', index_col=0)
        else:
            tickers = pd.DataFrame.from_records(tickers).sort_values(by='symbol', axis=1, ignore_index=True)

        for symbol, name in tickers.itertuples(index=False):
            if not re.match(r'A\d{5}', symbol):
                self.redis.hset('tickers', symbol, name)
                self.redis.hset('tickers', name, symbol)

    def update_metas(self, stock):
        self.switch_db(1)
        self.redis.hset('metas', stock['symbol'], json.dumps(stock))

    def get_metas(self, stock_id: str) -> dict or None:
        self.switch_db(1)
        ticker = self.redis.hget('metas', stock_id)

        if ticker is not None:
            ticker = json.loads(ticker)

        return ticker

    def request_limiter_setter(self, request_id, db_index=1, expire_time=60, throttle=60):
        self.redis.select(db_index)
        if self.redis.get(request_id) is None:
            self.redis.set(request_id, 1, ex=expire_time)
            return

        if int(self.redis.get(request_id)) > throttle:
            raise ValueError("Too Many Requests, cool down remaining: {0} seconds".format(self.redis.ttl(request_id)))

        current_throttle = int(self.redis.get(request_id))
        current_ttl = int(self.redis.ttl(request_id))
        self.redis.set(request_id, current_throttle + 1, ex=current_ttl)
