import ccxt
import logging
from .database import DatabaseManager
from .cache import Cache
import pybreaker

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.db = DatabaseManager()
        self.cache = Cache()
        self.breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

    async def collect_btc_data(self, symbol="BTC/USDT", timeframe="1h", limit=100):
        """Fetch market data from the exchange and store it"""
        try:
            cache_key = f"ohlcv:{symbol}:{timeframe}"
            data = self.cache.get_json(cache_key)
            if not data:
                ohlcv = self.breaker.call(self.exchange.fetch_ohlcv, symbol, timeframe, limit)
                self.cache.set_json(cache_key, ohlcv, ttl=300)
            else:
                ohlcv = data

            self.db.store_market_data(symbol, timeframe, ohlcv)
        except Exception as e:
            logger.error(f"Error collecting market data: {e}")

