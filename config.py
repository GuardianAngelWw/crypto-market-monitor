"""
Configuration file for Crypto Market Monitor
"""

import os
from datetime import time

# API Credentials - These can be set as environment variables or left as None for demo mode
BYBIT_API_KEY = os.environ.get('BYBIT_API_KEY')
BYBIT_API_SECRET = os.environ.get('BYBIT_API_SECRET')
GOOGLE_SHEETS_CREDS = os.environ.get('GOOGLE_SHEETS_CREDS')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS', '').split(',')
TRADING_ECONOMICS_KEY = os.environ.get('TRADING_ECONOMICS_KEY')

# Demo mode settings - used when API credentials are not available
DEMO_MODE = any(cred is None for cred in [BYBIT_API_KEY, BYBIT_API_SECRET, TRADING_ECONOMICS_KEY])

# Mock data for demo mode
MOCK_PRICES = {
    'BTCUSDT': 62430.45,
    'ETHUSDT': 3785.22,
    'SOLUSDT': 148.75,
    'XRPUSDT': 0.59,
    'BNBUSDT': 585.35
}

# Google Sheets Configuration
SPREADSHEET_ID = '1yQRWSt7bAv0u2MmzWtfD5TkfMCZl7PHMynTAViWUtRg'
TRADING_DATA_RANGE = 'Sheet1!A2:J100'
ECONOMIC_EVENTS_RANGE = 'Sheet1!A22:H100'

# Trading Pairs
PAIRS = [
    'BTCUSDT',
    'ETHUSDT',
    'SOLUSDT',
    'XRPUSDT',
    'BNBUSDT'
]

# Volatility Calculation
WINDOW_SIZE = 14  # Days for volatility calculation
VOLATILITY_WEIGHTS = {
    'hv': 0.3,      # Historical Volatility
    'atr': 0.3,     # Average True Range
    'bbw': 0.2,     # Bollinger Bands Width
    'event': 0.2    # Event Impact
}

# Scheduling
REPORT_TIME = time(8, 0)  # 8:00 UTC

# Trading Recommendation Rules
TRADING_RULES = [
    {'vol_min': 0.8, 'vol_max': 1.0, 'event_min': 0.7, 'event_max': 1.0, 'action': 'HOLD', 'risk': 'Extreme'},
    {'vol_min': 0.8, 'vol_max': 1.0, 'event_min': 0.0, 'event_max': 0.7, 'action': 'SCALP ONLY', 'risk': 'Very High'},
    {'vol_min': 0.6, 'vol_max': 0.8, 'event_min': 0.6, 'event_max': 1.0, 'action': 'REDUCE EXPOSURE', 'risk': 'High'},
    {'vol_min': 0.6, 'vol_max': 0.8, 'event_min': 0.0, 'event_max': 0.6, 'action': 'TRADE WITH CAUTION', 'risk': 'Elevated'},
    {'vol_min': 0.4, 'vol_max': 0.6, 'event_min': 0.5, 'event_max': 1.0, 'action': 'SELECTIVE TRADING', 'risk': 'Moderate'},
    {'vol_min': 0.4, 'vol_max': 0.6, 'event_min': 0.0, 'event_max': 0.5, 'action': 'TRADE NORMALLY', 'risk': 'Normal'},
    {'vol_min': 0.2, 'vol_max': 0.4, 'event_min': 0.6, 'event_max': 1.0, 'action': 'PREPARE FOR VOLATILITY', 'risk': 'Low but increasing'},
    {'vol_min': 0.2, 'vol_max': 0.4, 'event_min': 0.0, 'event_max': 0.6, 'action': 'LONGER TIMEFRAMES', 'risk': 'Low'},
    {'vol_min': 0.0, 'vol_max': 0.2, 'event_min': 0.5, 'event_max': 1.0, 'action': 'PREPARE FOR BREAKOUTS', 'risk': 'Very Low but watch'},
    {'vol_min': 0.0, 'vol_max': 0.2, 'event_min': 0.0, 'event_max': 0.5, 'action': 'RANGE TRADING', 'risk': 'Very Low'}
]

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIRECTORY = 'logs'