"""
Database Manager - Handles data storage and retrieval
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='data/trading_bot.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Market data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        symbol TEXT,
                        timeframe TEXT,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Analysis results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        analysis_type TEXT,
                        result TEXT, -- JSON string
                        confidence INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Research data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS research_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT,
                        title TEXT,
                        content TEXT,
                        url TEXT,
                        sentiment TEXT,
                        relevance_score REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Model performance table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS model_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT,
                        accuracy REAL,
                        precision_score REAL,
                        recall_score REAL,
                        test_date DATETIME,
                        parameters TEXT, -- JSON string
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Trading signals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trading_signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        signal_type TEXT, -- buy/sell/hold
                        entry_price REAL,
                        exit_price REAL,
                        stop_loss REAL,
                        take_profit REAL,
                        confidence INTEGER,
                        status TEXT, -- active/closed/cancelled
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            
    def store_market_data(self, symbol, timeframe, ohlcv_data):
        """Store market data in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for candle in ohlcv_data:
                    timestamp = datetime.fromtimestamp(candle[0] / 1000)
                    cursor.execute('''
                        INSERT OR REPLACE INTO market_data 
                        (timestamp, symbol, timeframe, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (timestamp, symbol, timeframe, candle[1], candle[2], candle[3], candle[4], candle[5]))
                
                conn.commit()
                logger.info(f"Stored {len(ohlcv_data)} candles for {symbol} {timeframe}")
                
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            
    def get_market_data(self, symbol, timeframe, limit=100):
        """Retrieve market data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT timestamp, open, high, low, close, volume
                    FROM market_data
                    WHERE symbol = ? AND timeframe = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                '''
                df = pd.read_sql_query(query, conn, params=(symbol, timeframe, limit))
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df.sort_values('timestamp').reset_index(drop=True)
                
        except Exception as e:
            logger.error(f"Error retrieving market data: {e}")
            return None
            
    def store_analysis_result(self, analysis_type, result, confidence):
        """Store analysis results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO analysis_results 
                    (timestamp, analysis_type, result, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (datetime.now(), analysis_type, json.dumps(result), confidence))
                
                conn.commit()
                logger.info(f"Stored {analysis_type} analysis result")
                
        except Exception as e:
            logger.error(f"Error storing analysis result: {e}")
            
    def get_latest_analysis(self, analysis_type, limit=1):
        """Get latest analysis results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, result, confidence
                    FROM analysis_results
                    WHERE analysis_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (analysis_type, limit))
                
                results = cursor.fetchall()
                
                parsed_results = []
                for row in results:
                    parsed_results.append({
                        'timestamp': row[0],
                        'result': json.loads(row[1]),
                        'confidence': row[2]
                    })
                    
                return parsed_results
                
        except Exception as e:
            logger.error(f"Error retrieving analysis results: {e}")
            return []
            
    def store_research_data(self, source, title, content, url, sentiment, relevance_score):
        """Store research data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO research_data 
                    (source, title, content, url, sentiment, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (source, title, content, url, sentiment, relevance_score))
                
                conn.