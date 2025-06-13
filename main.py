#!/usr/bin/env python3
"""
Crypto Market Monitor
---------------------
Monitors economic calendar events, analyzes market volatility, and provides
daily trading recommendations for cryptocurrency markets on Bybit.
"""

import os
import json
import time
import hmac
import hashlib
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
BYBIT_API_KEY = os.environ.get('BYBIT_API_KEY')
BYBIT_API_SECRET = os.environ.get('BYBIT_API_SECRET')
GOOGLE_SHEETS_CREDS = os.environ.get('GOOGLE_SHEETS_CREDS')
SPREADSHEET_ID = '1yQRWSt7bAv0u2MmzWtfD5TkfMCZl7PHMynTAViWUtRg'
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

# Constants
WINDOW_SIZE = 14  # Days for volatility calculation
PAIRS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'BNBUSDT']
VOLATILITY_WEIGHTS = {
    'hv': 0.3,      # Historical Volatility
    'atr': 0.3,     # Average True Range
    'bbw': 0.2,     # Bollinger Bands Width
    'event': 0.2    # Event Impact
}

class BybitAPI:
    """Interface for the Bybit cryptocurrency exchange API"""
    
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.bybit.com'
    
    def _generate_signature(self, params, timestamp):
        """Generate HMAC signature for API authentication"""
        param_str = timestamp + self.api_key + str(params)
        return hmac.new(
            bytes(self.api_secret, 'utf-8'),
            bytes(param_str, 'utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def get_klines(self, symbol, interval='D', limit=200):
        """Get candlestick data for a symbol"""
        endpoint = '/v2/public/kline/list'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"Error fetching klines: {response.text}")
            return []
    
    def get_orderbook(self, symbol):
        """Get order book data for a symbol"""
        endpoint = '/v2/public/orderBook/L2'
        params = {'symbol': symbol}
        
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"Error fetching orderbook: {response.text}")
            return []

class EconomicCalendar:
    """Fetches economic calendar events from various sources"""
    
    def __init__(self):
        self.base_url = 'https://api.tradingeconomics.com/calendar'
        self.api_key = os.environ.get('TRADING_ECONOMICS_KEY')
    
    def get_events(self, days=7):
        """Get economic calendar events for the next X days"""
        # This is a simplified example - in production, use actual API credentials
        # or web scraping with proper permissions
        
        today = datetime.now()
        end_date = today + timedelta(days=days)
        
        try:
            # For simulation purposes, we'll create mock data
            # In production, use:
            # response = requests.get(f"{self.base_url}/country/all/{today.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?c={self.api_key}")
            
            # Mock data
            mock_events = [
                {
                    'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'event': 'FOMC Meeting Minutes',
                    'country': 'United States',
                    'impact': 'High',
                    'forecast': 'N/A',
                    'previous': 'N/A',
                    'actual': '',
                    'time': '18:00'
                },
                {
                    'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'event': 'ECB Interest Rate Decision',
                    'country': 'Eurozone',
                    'impact': 'High',
                    'forecast': '3.75%',
                    'previous': '3.75%',
                    'actual': '',
                    'time': '12:45'
                },
                {
                    'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'event': 'US Nonfarm Payrolls',
                    'country': 'United States',
                    'impact': 'High',
                    'forecast': '180K',
                    'previous': '175K',
                    'actual': '',
                    'time': '13:30'
                },
                {
                    'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'event': 'Japan GDP Growth Rate QoQ',
                    'country': 'Japan',
                    'impact': 'Medium',
                    'forecast': '0.4%',
                    'previous': '0.3%',
                    'actual': '',
                    'time': '00:50'
                },
                {
                    'date': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
                    'event': 'China Manufacturing PMI',
                    'country': 'China',
                    'impact': 'Medium',
                    'forecast': '50.3',
                    'previous': '50.1',
                    'actual': '',
                    'time': '01:30'
                }
            ]
            
            return mock_events
        except Exception as e:
            print(f"Error fetching economic events: {e}")
            return []

class VolatilityAnalyzer:
    """Analyzes market volatility using various indicators"""
    
    def __init__(self, klines_data):
        """Initialize with klines data (candlestick data)"""
        self.df = self._prepare_dataframe(klines_data)
    
    def _prepare_dataframe(self, klines_data):
        """Convert klines data to pandas DataFrame"""
        df = pd.DataFrame(klines_data)
        df['time'] = pd.to_datetime(df['open_time'], unit='s')
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df.set_index('time', inplace=True)
        return df
    
    def calculate_historical_volatility(self, window=WINDOW_SIZE):
        """Calculate historical volatility (standard deviation of returns)"""
        if len(self.df) < window:
            return None
        
        # Calculate log returns
        self.df['returns'] = np.log(self.df['close'] / self.df['close'].shift(1))
        
        # Calculate historical volatility (annualized)
        hv = self.df['returns'].rolling(window=window).std() * np.sqrt(365)
        
        return hv.iloc[-1] if not hv.empty else None
    
    def calculate_atr(self, window=WINDOW_SIZE):
        """Calculate Average True Range"""
        if len(self.df) < window:
            return None
        
        # Calculate True Range
        self.df['tr0'] = abs(self.df['high'] - self.df['low'])
        self.df['tr1'] = abs(self.df['high'] - self.df['close'].shift(1))
        self.df['tr2'] = abs(self.df['low'] - self.df['close'].shift(1))
        self.df['tr'] = self.df[['tr0', 'tr1', 'tr2']].max(axis=1)
        
        # Calculate ATR
        self.df['atr'] = self.df['tr'].rolling(window=window).mean()
        
        # Normalize ATR by price to get percentage
        atr_pct = self.df['atr'].iloc[-1] / self.df['close'].iloc[-1]
        
        return atr_pct
    
    def calculate_bbw(self, window=WINDOW_SIZE, num_std=2):
        """Calculate Bollinger Bands Width"""
        if len(self.df) < window:
            return None
        
        # Calculate SMA and standard deviation
        self.df['sma'] = self.df['close'].rolling(window=window).mean()
        self.df['std'] = self.df['close'].rolling(window=window).std()
        
        # Calculate Bollinger Bands
        self.df['upper_band'] = self.df['sma'] + (self.df['std'] * num_std)
        self.df['lower_band'] = self.df['sma'] - (self.df['std'] * num_std)
        
        # Calculate Bollinger Bands Width (normalized)
        self.df['bbw'] = (self.df['upper_band'] - self.df['lower_band']) / self.df['sma']
        
        return self.df['bbw'].iloc[-1] if not self.df['bbw'].empty else None

class TradingRecommendation:
    """Generates trading recommendations based on volatility and events"""
    
    def __init__(self, volatility_score, events):
        self.volatility_score = volatility_score
        self.events = events
        
    def _calculate_event_impact(self):
        """Calculate event impact score based on upcoming events"""
        # Simple scoring: High=1.0, Medium=0.5, Low=0.25
        impact_map = {'High': 1.0, 'Medium': 0.5, 'Low': 0.25}
        
        # Calculate total impact, weighting events by how soon they occur
        total_impact = 0
        today = datetime.now().date()
        
        for event in self.events:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
            days_until = (event_date - today).days
            
            # Events happening sooner have more impact
            time_weight = max(0, (7 - days_until) / 7)
            event_impact = impact_map.get(event['impact'], 0) * time_weight
            total_impact += event_impact
        
        # Normalize to 0-1 scale
        return min(1.0, total_impact / 3.0)
    
    def generate_recommendation(self):
        """Generate trading recommendation based on volatility and events"""
        event_impact = self._calculate_event_impact()
        
        # Trading recommendation rules based on volatility score and event impact
        if self.volatility_score > 0.8:
            if event_impact > 0.7:
                action = "HOLD"
                risk = "Extreme"
                strategy = "Avoid new positions due to extreme volatility and high-impact events"
            else:
                action = "SCALP ONLY"
                risk = "Very High"
                strategy = "Short-term scalping only with tight stop losses"
        
        elif self.volatility_score > 0.6:
            if event_impact > 0.6:
                action = "REDUCE EXPOSURE"
                risk = "High"
                strategy = "Reduce position sizes and set tighter stop losses"
            else:
                action = "TRADE WITH CAUTION"
                risk = "Elevated"
                strategy = "Trade with reduced position sizes"
        
        elif self.volatility_score > 0.4:
            if event_impact > 0.5:
                action = "SELECTIVE TRADING"
                risk = "Moderate"
                strategy = "Focus on strongest setups and major support/resistance levels"
            else:
                action = "TRADE NORMALLY"
                risk = "Normal"
                strategy = "Standard position sizing and risk management"
        
        elif self.volatility_score > 0.2:
            if event_impact > 0.6:
                action = "PREPARE FOR VOLATILITY"
                risk = "Low but increasing"
                strategy = "Position for potential volatility increase after events"
            else:
                action = "LONGER TIMEFRAMES"
                risk = "Low"
                strategy = "Focus on longer timeframe setups with wider stops"
        
        else:
            if event_impact > 0.5:
                action = "PREPARE FOR BREAKOUTS"
                risk = "Very Low but watch events"
                strategy = "Look for breakout setups triggered by upcoming events"
            else:
                action = "RANGE TRADING"
                risk = "Very Low"
                strategy = "Focus on range-bound strategies and accumulation"
        
        return {
            "action": action,
            "risk_level": risk,
            "strategy": strategy,
            "volatility_score": self.volatility_score,
            "event_impact": event_impact
        }

class GoogleSheetsManager:
    """Manages interactions with Google Sheets"""
    
    def __init__(self, creds_json, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # In production, load creds from environment or file
        # Here we simulate for the workflow
        try:
            # creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), self.scope)
            # self.client = gspread.authorize(creds)
            # self.sheet = self.client.open_by_key(spreadsheet_id)
            print("Connected to Google Sheets (simulated)")
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
    
    def update_trading_data(self, date, trading_data):
        """Update trading data in the spreadsheet"""
        # In a real implementation, this would write to the Google Sheet
        print(f"Updating trading data for {date}:")
        for pair, data in trading_data.items():
            print(f"  {pair}: Volatility Score = {data['volatility_score']:.2f}, Recommendation = {data['recommendation']['action']}")
    
    def update_economic_events(self, events):
        """Update economic events in the spreadsheet"""
        # In a real implementation, this would write to the Google Sheet
        print(f"Updating economic events:")
        for event in events:
            print(f"  {event['date']} - {event['event']} ({event['impact']} impact)")

class EmailNotifier:
    """Sends email notifications with trading recommendations"""
    
    def __init__(self, sender, password, recipients):
        self.sender = sender
        self.password = password
        self.recipients = recipients
    
    def send_daily_report(self, trading_data, events, date):
        """Send daily trading report via email"""
        # In production, this would send an actual email
        # Here we'll print the email content for the workflow
        
        subject = f"Crypto Trading Recommendations - {date}"
        
        # Build HTML email body
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #4b6cb7; color: white; padding: 10px; }}
                .section {{ margin: 15px 0; padding: 10px; border: 1px solid #ddd; }}
                .event-high {{ color: #d32f2f; }}
                .event-medium {{ color: #f57c00; }}
                .event-low {{ color: #388e3c; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Crypto Trading Recommendations - {date}</h2>
            </div>
            
            <div class="section">
                <h3>⚠️ Upcoming Economic Events</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Time (UTC)</th>
                        <th>Event</th>
                        <th>Country</th>
                        <th>Impact</th>
                    </tr>
        """
        
        # Add event rows
        for event in events[:5]:  # Show top 5 events
            impact_class = f"event-{event['impact'].lower()}"
            html += f"""
                    <tr>
                        <td>{event['date']}</td>
                        <td>{event['time']}</td>
                        <td>{event['event']}</td>
                        <td>{event['country']}</td>
                        <td class="{impact_class}">{event['impact']}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h3>📊 Volatility Forecast</h3>
                <table>
                    <tr>
                        <th>Asset</th>
                        <th>Current Price</th>
                        <th>Volatility Score</th>
                        <th>Recommendation</th>
                        <th>Risk Level</th>
                    </tr>
        """
        
        # Add trading data rows
        for pair, data in trading_data.items():
            html += f"""
                    <tr>
                        <td>{pair}</td>
                        <td>${data['price']:.2f}</td>
                        <td>{data['volatility_score']:.2f}</td>
                        <td>{data['recommendation']['action']}</td>
                        <td>{data['recommendation']['risk_level']}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h3>💡 Market Insights</h3>
                <p>Based on current volatility metrics and upcoming economic events, the market shows the following characteristics:</p>
                <ul>
        """
        
        # Add market insights
        overall_vol = sum(data['volatility_score'] for data in trading_data.values()) / len(trading_data)
        if overall_vol > 0.6:
            html += "<li>Markets are experiencing elevated volatility, suggesting potential for significant price swings.</li>"
        elif overall_vol < 0.3:
            html += "<li>Markets are in a low volatility regime, potentially building energy for future directional moves.</li>"
        else:
            html += "<li>Markets are showing moderate volatility, suitable for standard trading approaches.</li>"
        
        # Add event-based insights
        high_impact_events = sum(1 for event in events if event['impact'] == 'High')
        if high_impact_events >= 2:
            html += "<li>Multiple high-impact economic events in the coming days may increase volatility.</li>"
        
        html += """
                </ul>
            </div>
            
            <div class="section">
                <h3>⚖️ Risk Assessment</h3>
                <p>Key factors to consider for risk management:</p>
                <ul>
        """
        
        # Add risk factors
        max_vol_pair = max(trading_data.items(), key=lambda x: x[1]['volatility_score'])
        html += f"<li>{max_vol_pair[0]} currently shows the highest volatility with a score of {max_vol_pair[1]['volatility_score']:.2f}.</li>"
        
        next_event = min(events, key=lambda e: datetime.strptime(e['date'], '%Y-%m-%d').date())
        html += f"<li>Next significant event: {next_event['event']} on {next_event['date']} ({next_event['impact']} impact).</li>"
        
        html += """
                </ul>
            </div>
            
            <p>This report is generated automatically based on market data and economic events. Always conduct your own analysis before making trading decisions.</p>
        </body>
        </html>
        """
        
        print("\n========= EMAIL CONTENT =========")
        print(f"SUBJECT: {subject}")
        print("BODY: [HTML content not displayed in console]")
        print("=================================\n")
        
        # In production, send the actual email
        # self._send_email(subject, html)
    
    def _send_email(self, subject, html_body):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.recipients)
            
            # Attach HTML content
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.recipients, msg.as_string())
            
            print("Email sent successfully")
        except Exception as e:
            print(f"Error sending email: {e}")

def main():
    """Main function to run the crypto market monitor"""
    print(f"Starting Crypto Market Monitor at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize API clients
    bybit = BybitAPI(BYBIT_API_KEY, BYBIT_API_SECRET)
    calendar = EconomicCalendar()
    sheets = GoogleSheetsManager(GOOGLE_SHEETS_CREDS, SPREADSHEET_ID)
    emailer = EmailNotifier(EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENTS)
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Fetch economic calendar events
    events = calendar.get_events(days=7)
    sheets.update_economic_events(events)
    
    # Process each trading pair
    trading_data = {}
    for pair in PAIRS:
        # Fetch klines data
        klines = bybit.get_klines(pair, limit=50)
        
        if not klines:
            print(f"No data available for {pair}, skipping...")
            continue
        
        # Analyze volatility
        analyzer = VolatilityAnalyzer(klines)
        hv = analyzer.calculate_historical_volatility() or 0
        atr = analyzer.calculate_atr() or 0
        bbw = analyzer.calculate_bbw() or 0
        
        # Calculate weighted volatility score (0-1 scale)
        vol_score = (
            VOLATILITY_WEIGHTS['hv'] * min(1.0, hv) +
            VOLATILITY_WEIGHTS['atr'] * min(1.0, atr * 10) +
            VOLATILITY_WEIGHTS['bbw'] * min(1.0, bbw * 5)
        )
        
        # Generate trading recommendation
        recommender = TradingRecommendation(vol_score, events)
        recommendation = recommender.generate_recommendation()
        
        # Add event impact to complete the volatility score
        vol_score = vol_score * (1 - VOLATILITY_WEIGHTS['event']) + recommendation['event_impact'] * VOLATILITY_WEIGHTS['event']
        
        # Store results
        trading_data[pair] = {
            'price': float(klines[0]['close']),
            'historical_volatility': hv,
            'atr': atr,
            'bbw': bbw,
            'volatility_score': vol_score,
            'recommendation': recommendation
        }
    
    # Update Google Sheets with trading data
    sheets.update_trading_data(today, trading_data)
    
    # Send email notification
    emailer.send_daily_report(trading_data, events, today)
    
    print(f"Crypto Market Monitor completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()