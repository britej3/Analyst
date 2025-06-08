"""
Chart Analyzer - Generates visual charts and analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import ccxt
import logging
import os

logger = logging.getLogger(__name__)

class ChartAnalyzer:
    def __init__(self):
        self.exchange = ccxt.binance()
        
    async def generate_analysis_chart(self):
        """Generate comprehensive analysis chart"""
        try:
            # Get market data
            ohlcv = self.exchange.fetch_ohlcv('BTC/USDT', '1h', limit=168)  # 1 week
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Calculate indicators
            df = self.calculate_chart_indicators(df)
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                subplot_titles=('BTCUSDT Price Action', 'Volume', 'RSI'),
                row_heights=[0.6, 0.2, 0.2]
            )
            
            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='BTCUSDT',
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4444'
                ),
                row=1, col=1
            )
            
            # Add moving averages
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['sma_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['ema_50'],
                    mode='lines',
                    name='EMA 50',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
            
            # Add Bollinger Bands
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='gray', width=1),
                    fill=None
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_lower'],
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='gray', width=1),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)'
                ),
                row=1, col=1
            )
            
            # Add support/resistance levels
            latest_high = df['high'].rolling(20).max().iloc[-1]
            latest_low = df['low'].rolling(20).min().iloc[-1]
            
            fig.add_hline(
                y=latest_high,
                line_dash="dash",
                line_color="red",
                annotation_text="Resistance",
                row=1, col=1
            )
            
            fig.add_hline(
                y=latest_low,
                line_dash="dash", 
                line_color="green",
                annotation_text="Support",
                row=1, col=1
            )
            
            # Add volume
            colors = ['green' if close >= open else 'red' for close, open in zip(df['close'], df['open'])]
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # Add RSI
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=2)
                ),
                row=3, col=1
            )
            
            # Add RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
            
            # Update layout
            fig.update_layout(
                title='BTCUSDT Technical Analysis',
                template='plotly_dark',
                height=800,
                showlegend=True,
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(title_text="Time", row=3, col=1)
            fig.update_yaxes(title_text="Price ($)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=3, col=1)
            
            # Save chart
            os.makedirs('data/charts', exist_ok=True)
            chart_path = f'data/charts/btcusdt_analysis_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
            fig.write_image(chart_path, width=1200, height=800)
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error generating analysis chart: {e}")
            # Return a simple error chart
            return await self.generate_error_chart()
            
    async def generate_error_chart(self):
        """Generate simple error chart"""
        try:
            fig = go.Figure()
            fig.add_annotation(
                text="Chart temporarily unavailable<br>Please try again later",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=20, color="white")
            )
            fig.update_layout(
                template='plotly_dark',
                height=400,
                width=600,
                title="BTCUSDT Analysis"
            )
            
            os.makedirs('data/charts', exist_ok=True)
            error_path = 'data/charts/error_chart.png'
            fig.write_image(error_path, width=600, height=400)
            return error_path
            
        except Exception as e:
            logger.error(f"Error generating error chart: {e}")
            return None
            
    def calculate_chart_indicators(self, df):
        """Calculate indicators for charting"""
        try:
            # Simple moving averages
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            
            # Exponential moving averages
            df['ema_20'] = df['close'].ewm(span=20).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(20).mean()
            bb_std = df['close'].rolling(20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # MACD
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating chart indicators: {e}")
            return df
            
    async def generate_prediction_chart(self, predictions):
        """Generate prediction visualization"""
        try:
            # Get current data
            ohlcv = self.exchange.fetch_ohlcv('BTC/USDT', '1h', limit=24)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Create future timestamps
            last_time = df['timestamp'].iloc[-1]
            future_times = [
                last_time + pd.Timedelta(hours=1),
                last_time + pd.Timedelta(hours=4),
                last_time + pd.Timedelta(hours=24)
            ]
            
            # Extract prediction values
            pred_prices = [
                float(predictions['1h']['price']),
                float(predictions['4h']['price']),
                float(predictions['24h']['price'])
            ]
            
            fig = go.Figure()
            
            # Add historical price
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['close'],
                    mode='lines',
                    name='Historical Price',
                    line=dict(color='white', width=2)
                )
            )
            
            # Add predictions
            fig.add_trace(
                go.Scatter(
                    x=future_times,
                    y=pred_prices,
                    mode='markers+lines',
                    name='Predictions',
                    line=dict(color='yellow', width=2, dash='dash'),
                    marker=dict(size=8, color='yellow')
                )
            )
            
            # Add current price point
            current_price = df['close'].iloc[-1]
            fig.add_trace(
                go.Scatter(
                    x=[df['timestamp'].iloc[-1]],
                    y=[current_price],
                    mode='markers',
                    name='Current Price',
                    marker=dict(size=12, color='red', symbol='circle')
                )
            )
            
            fig.update_layout(
                title='BTCUSDT Price Predictions',
                template='plotly_dark',
                height=500,
                xaxis_title='Time',
                yaxis_title='Price ($)',
                showlegend=True
            )
            
            # Save prediction chart
            os.makedirs('data/charts', exist_ok=True)
            pred_path = f'data/charts/btcusdt_predictions_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
            fig.write_image(pred_path, width=1000, height=500)
            
            return pred_path
            
        except Exception as e:
            logger.error(f"Error generating prediction chart: {e}")
            return None