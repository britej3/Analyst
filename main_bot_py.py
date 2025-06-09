#!/usr/bin/env python3
"""
AI Trading Research Bot - Main Application
Continuously learning AI agent for BTCUSDT analysis
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

from src.researcher import TradingResearcher
from src.data_collector import DataCollector
from src.ai_analyst import AIAnalyst
from src.chart_analyzer import ChartAnalyzer
from src.database import DatabaseManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        self.researcher = TradingResearcher()
        self.data_collector = DataCollector()
        self.ai_analyst = AIAnalyst()
        self.chart_analyzer = ChartAnalyzer()
        self.db = DatabaseManager()
        
        # Initialize components
        self.setup_components()
        
    def setup_components(self):
        """Initialize all bot components"""
        logger.info("Initializing trading bot components...")
        asyncio.create_task(self.start_background_tasks())
        
    async def start_background_tasks(self):
        """Start continuous learning and data collection"""
        # Start data collection every 5 minutes
        asyncio.create_task(self.continuous_data_collection())
        # Start research updates every hour
        asyncio.create_task(self.continuous_research())
        # Start model training every 6 hours
        asyncio.create_task(self.continuous_learning())
        
    async def continuous_data_collection(self):
        """Collect market data continuously"""
        while True:
            try:
                await self.data_collector.collect_btc_data()
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Data collection error: {e}")
                await asyncio.sleep(60)
                
    async def continuous_research(self):
        """Research new strategies and updates"""
        while True:
            try:
                await self.researcher.research_new_strategies()
                await self.researcher.update_knowledge_base()
                await asyncio.sleep(3600)  # 1 hour
            except Exception as e:
                logger.error(f"Research error: {e}")
                await asyncio.sleep(300)
                
    async def continuous_learning(self):
        """Retrain models with new data"""
        while True:
            try:
                await self.ai_analyst.retrain_models()
                await asyncio.sleep(21600)  # 6 hours
            except Exception as e:
                logger.error(f"Learning error: {e}")
                await asyncio.sleep(1800)

    # Telegram Bot Handlers
    async def start(self, update: Update, context):
        """Start command handler"""
        keyboard = [
            [InlineKeyboardButton("📊 Current Analysis", callback_data='analysis')],
            [InlineKeyboardButton("📈 Price Prediction", callback_data='prediction')],
            [InlineKeyboardButton("🔍 Market Research", callback_data='research')],
            [InlineKeyboardButton("⚙️ Settings", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *AI Trading Researcher Bot*\n\n"
            "I'm continuously learning and analyzing BTCUSDT markets.\n"
            "What would you like to know?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_handler(self, update: Update, context):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'analysis':
            await self.send_current_analysis(query)
        elif query.data == 'prediction':
            await self.send_price_prediction(query)
        elif query.data == 'research':
            await self.send_latest_research(query)
        elif query.data == 'settings':
            await self.send_settings(query)
            
    async def send_current_analysis(self, query):
        """Send current market analysis"""
        try:
            # Get latest analysis from AI
            analysis = await self.ai_analyst.get_current_analysis()
            chart_path = await self.chart_analyzer.generate_analysis_chart()
            
            message = f"""
📊 *Current BTCUSDT Analysis*

🔍 **Technical Analysis:**
{analysis['technical']}

📈 **Price Action:**
{analysis['price_action']}

💰 **Entry/Exit Levels:**
{analysis['levels']}

🎯 **Confidence:** {analysis['confidence']}%

⏰ *Updated: {datetime.now().strftime('%H:%M UTC')}*
            """
            
            # Send chart first
            with open(chart_path, 'rb') as chart:
                await query.message.reply_photo(
                    photo=chart,
                    caption=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            await query.message.reply_text(f"Error generating analysis: {e}")
            
    async def send_price_prediction(self, query):
        """Send price predictions"""
        try:
            predictions = await self.ai_analyst.get_price_predictions()
            
            message = f"""
🔮 *BTCUSDT Price Predictions*

⏱️ **Next 1 Hour:** ${predictions['1h']['price']} ({predictions['1h']['change']})
📅 **Next 4 Hours:** ${predictions['4h']['price']} ({predictions['4h']['change']})
🗓️ **Next 24 Hours:** ${predictions['24h']['price']} ({predictions['24h']['change']})

🎯 **Model Accuracy:** {predictions['accuracy']}%
📊 **Based on:** {predictions['factors']}

⚠️ *This is not financial advice*
            """
            
            await query.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await query.message.reply_text(f"Error generating predictions: {e}")
            
    async def send_latest_research(self, query):
        """Send latest research findings"""
        try:
            research = await self.researcher.get_latest_findings()
            
            message = f"""
🔬 *Latest Research Findings*

📰 **Market News Impact:**
{research['news_impact']}

📊 **New Patterns Discovered:**
{research['patterns']}

🧠 **Strategy Updates:**
{research['strategy_updates']}

📈 **Performance Metrics:**
{research['performance']}

🔄 *Last Updated: {research['timestamp']}*
            """
            
            await query.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await query.message.reply_text(f"Error fetching research: {e}")

    def run(self):
        """Start the bot"""
        app = Application.builder().token(self.token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CallbackQueryHandler(self.button_handler))
        
        logger.info("Bot starting...")
        app.run_polling()

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
