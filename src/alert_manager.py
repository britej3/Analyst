import asyncio
import logging
from .data_collector import DataCollector

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold
        self.last_price = None
        self.collector = DataCollector()

    async def monitor_price(self, notify_callback):
        while True:
            try:
                await self.collector.collect_btc_data(limit=1)
                data = self.collector.db.get_market_data('BTC/USDT', '1h', limit=1)
                price = data['close'].iloc[-1]
                if self.last_price is not None:
                    change = abs(price - self.last_price) / self.last_price * 100
                    if change >= self.threshold:
                        await notify_callback(price, change)
                self.last_price = price
            except Exception as e:
                logger.error(f"Alert monitor error: {e}")
            await asyncio.sleep(300)

