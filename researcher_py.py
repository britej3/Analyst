"""
AI Trading Researcher - Continuously learns from verified sources
"""

import asyncio
import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class TradingResearcher:
    def __init__(self):
        self.verified_sources = {
            'news': [
                'https://cointelegraph.com/rss',
                'https://coindesk.com/arc/outboundfeeds/rss/',
                'https://cryptonews.com/news/feed/',
                'https://bitcoinmagazine.com/.rss/full/'
            ],
            'analysis': [
                'https://www.tradingview.com/symbols/BTCUSDT/',
                'https://www.coinglass.com/pro/i/BTC',
                'https://alternative.me/crypto/fear-and-greed-index/'
            ],
            'research': [
                'https://research.binance.com/',
                'https://insights.glassnode.com/',
                'https://coinmetrics.io/insights/'
            ]
        }
        
        self.knowledge_base = {}
        self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """Load existing knowledge base"""
        try:
            if os.path.exists('data/knowledge_base.json'):
                with open('data/knowledge_base.json', 'r') as f:
                    self.knowledge_base = json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_base = {}
            
    def save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/knowledge_base.json', 'w') as f:
                json.dump(self.knowledge_base, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            
    async def research_new_strategies(self):
        """Research new trading strategies from verified sources"""
        logger.info("Starting strategy research...")
        
        strategies = []
        
        # Collect from news sources
        for source in self.verified_sources['news']:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries[:5]:  # Latest 5 articles
                    if any(keyword in entry.title.lower() for keyword in 
                          ['bitcoin', 'btc', 'trading', 'analysis', 'prediction']):
                        strategies.append({
                            'title': entry.title,
                            'summary': entry.summary if hasattr(entry, 'summary') else '',
                            'link': entry.link,
                            'published': entry.published if hasattr(entry, 'published') else '',
                            'source': source,
                            'type': 'news'
                        })
            except Exception as e:
                logger.error(f"Error fetching from {source}: {e}")
                
        # Process and analyze strategies
        await self.process_strategies(strategies)
        
    async def process_strategies(self, strategies: List[Dict]):
        """Process and analyze new strategies using local LLM"""
        try:
            # Use local Ollama for analysis
            import requests
            
            for strategy in strategies:
                # Analyze with local LLM
                prompt = f"""
                Analyze this trading-related content for BTCUSDT:
                Title: {strategy['title']}
                Summary: {strategy['summary']}
                
                Extract:
                1. Trading signals or patterns mentioned
                2. Price predictions or targets
                3. Technical indicators discussed
                4. Risk factors mentioned
                5. Overall sentiment (bullish/bearish/neutral)
                
                Respond in JSON format.
                """
                
                response = requests.post('http://localhost:11434/api/generate', json={
                    'model': 'llama3.1:8b',
                    'prompt': prompt,
                    'stream': False
                })
                
                if response.status_code == 200:
                    analysis = response.json()['response']
                    strategy['ai_analysis'] = analysis
                    
            # Update knowledge base
            timestamp = datetime.now().isoformat()
            if 'strategies' not in self.knowledge_base:
                self.knowledge_base['strategies'] = []
                
            self.knowledge_base['strategies'].extend(strategies)
            self.knowledge_base['last_research_update'] = timestamp
            
            self.save_knowledge_base()
            logger.info(f"Processed {len(strategies)} new strategies")
            
        except Exception as e:
            logger.error(f"Error processing strategies: {e}")
            
    async def get_market_sentiment(self):
        """Get current market sentiment from multiple sources"""
        try:
            # Fear & Greed Index
            response = requests.get('https://api.alternative.me/fng/')
            fear_greed = response.json()['data'][0] if response.status_code == 200 else None
            
            # Social sentiment (simplified)
            sentiment_data = {
                'fear_greed_index': fear_greed,
                'timestamp': datetime.now().isoformat(),
                'social_sentiment': await self.analyze_social_sentiment()
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return None
            
    async def analyze_social_sentiment(self):
        """Analyze social media sentiment (placeholder)"""
        # This would integrate with Twitter API, Reddit API, etc.
        # For now, return mock data
        return {
            'twitter_sentiment': 0.65,  # 0-1 scale
            'reddit_sentiment': 0.58,
            'overall_sentiment': 0.62
        }
        
    async def update_knowledge_base(self):
        """Update knowledge base with latest market data"""
        try:
            # Get latest market data
            market_data = await self.get_latest_market_data()
            sentiment = await self.get_market_sentiment()
            
            # Update knowledge base
            self.knowledge_base['market_data'] = market_data
            self.knowledge_base['sentiment'] = sentiment
            self.knowledge_base['last_update'] = datetime.now().isoformat()
            
            self.save_knowledge_base()
            logger.info("Knowledge base updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
            
    async def get_latest_market_data(self):
        """Get latest BTCUSDT market data"""
        try:
            # Binance API for real-time data
            response = requests.get('https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT')
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
            
    async def get_latest_findings(self):
        """Get latest research findings for telegram bot"""
        try:
            if not self.knowledge_base:
                return {
                    'news_impact': 'No recent data available',
                    'patterns': 'Analyzing...',
                    'strategy_updates': 'Learning in progress',
                    'performance': 'Initializing...',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                }
                
            # Extract latest findings
            latest_strategies = self.knowledge_base.get('strategies', [])[-3:]  # Last 3
            market_data = self.knowledge_base.get('market_data', {})
            sentiment = self.knowledge_base.get('sentiment', {})
            
            findings = {
                'news_impact': self.summarize_news_impact(latest_strategies),
                'patterns': self.identify_patterns(market_data),
                'strategy_updates': self.get_strategy_updates(latest_strategies),
                'performance': self.get_performance_metrics(),
                'timestamp': self.knowledge_base.get('last_update', 'Unknown')
            }
            
            return findings
            
        except Exception as e:
            logger.error(f"Error getting latest findings: {e}")
            return {
                'news_impact': f'Error: {e}',
                'patterns': 'Analysis temporarily unavailable',
                'strategy_updates': 'Please try again later',
                'performance': 'Data processing...',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
            }
            
    def summarize_news_impact(self, strategies):
        """Summarize impact of latest news"""
        if not strategies:
            return "No recent news analyzed"
            
        bullish_count = sum(1 for s in strategies if 'bullish' in str(s).lower())
        bearish_count = sum(1 for s in strategies if 'bearish' in str(s).lower())
        
        if bullish_count > bearish_count:
            return f"📈 Bullish sentiment from {len(strategies)} sources"
        elif bearish_count > bullish_count:
            return f"📉 Bearish sentiment from {len(strategies)} sources"
        else:
            return f"⚖️ Mixed sentiment from {len(strategies)} sources"
            
    def identify_patterns(self, market_data):
        """Identify current market patterns"""
        if not market_data:
            return "Pattern analysis in progress..."
            
        try:
            price_change = float(market_data.get('priceChangePercent', 0))
            volume_change = float(market_data.get('count', 0))  # trade count as proxy for volume change
            
            if price_change > 5:
                return f"🚀 Strong bullish momentum (+{price_change:.2f}%)"
            elif price_change < -5:
                return f"📉 Strong bearish momentum ({price_change:.2f}%)"
            else:
                return f"🔄 Consolidation phase ({price_change:.2f}%)"
                
        except Exception:
            return "Pattern recognition ongoing..."
            
    def get_strategy_updates(self, strategies):
        """Get strategy updates"""
        if not strategies:
            return "Learning new strategies..."
            
        return f"📊 Analyzed {len(strategies)} new sources\n🧠 Strategy database expanding"
        
    def get_performance_metrics(self):
        """Get performance metrics"""
        total_strategies = len(self.knowledge_base.get('strategies', []))
        return f"📈 {total_strategies} strategies analyzed\n🎯 Knowledge base growing"