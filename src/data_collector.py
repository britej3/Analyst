import ccxt
import logging
from .database import DatabaseManager

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.db = DatabaseManager()

    async def collect_btc_data(self, symbol="BTC/USDT", timeframe="1h", limit=100):
        """Fetch market data from the exchange and store it"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            self.db.store_market_data(symbol, timeframe, ohlcv)
        except Exception as e:
            logger.error(f"Error collecting market data: {e}")

