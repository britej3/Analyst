import json
import os
from typing import List, Dict
from datetime import datetime

class PortfolioManager:
    def __init__(self, path: str = 'data/portfolio.json'):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({'trades': []}, f)

    def _load(self) -> Dict:
        with open(self.path, 'r') as f:
            return json.load(f)

    def _save(self, data: Dict) -> None:
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def add_trade(self, symbol: str, side: str, quantity: float, price: float) -> None:
        data = self._load()
        data['trades'].append({
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'side': side,
            'qty': quantity,
            'price': price
        })
        self._save(data)

    def get_summary(self) -> Dict:
        data = self._load()
        return {
            'total_trades': len(data['trades']),
            'last_trade': data['trades'][-1] if data['trades'] else None
        }

