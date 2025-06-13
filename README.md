# Crypto Market Monitor

A cryptocurrency market monitoring system that calculates volatility scores, tracks economic events, and provides trading recommendations based on current market conditions.

## Features

- **Economic Calendar Integration**: Fetches and categorizes economic events by impact level (High/Medium/Low)
- **Market Data Analysis**: Collects and processes price, volume, and order book data from Bybit
- **Multi-Factor Volatility Assessment**: Combines Historical Volatility, ATR, Bollinger Bands Width, and Event Impact
- **Trading Recommendations**: Generates actionable trading advice based on market conditions
- **Automated Reporting**: Sends daily email reports and updates Google Sheets for tracking

## Setup Instructions

### Basic Setup (Demo Mode)

1. Clone the repository:
   ```
   git clone https://github.com/GuardianAngelWw/crypto-market-monitor.git
   cd crypto-market-monitor
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run in demo mode:
   ```
   python main.py
   ```
   
In demo mode, the system will use mock data and will not require API keys.

### Full Production Setup

For production use with real-time data, you'll need the following API keys:

#### 1. Bybit API Keys
1. Log into your [Bybit](https://www.bybit.com/) account
2. Click on the profile icon in the top right corner
3. Select "API Management"
4. Click "Create New Key"
5. Configure permissions (Read permission is sufficient)
6. Complete 2FA verification and save your API key and secret

#### 2. Trading Economics API
1. Go to [Trading Economics API](https://tradingeconomics.com/api/) 
2. Sign up for an account
3. Navigate to the pricing section and subscribe to a plan
4. Your API key will be provided in your account dashboard

#### 3. Google Sheets API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Navigate to "APIs & Services" > "Credentials"
5. Click "Create credentials" > "Service account"
6. Follow the prompts and download the JSON credentials file
7. Share your Google Sheet with the email address in the service account

#### 4. Environment Variables

Set the following environment variables:

```
BYBIT_API_KEY=your_bybit_api_key
BYBIT_API_SECRET=your_bybit_api_secret
GOOGLE_SHEETS_CREDS=path/to/credentials.json
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
TRADING_ECONOMICS_KEY=your_trading_economics_key
```

For Gmail, use an App Password instead of your regular password.

## Components

- **BybitAPI**: Interface for interacting with the Bybit cryptocurrency exchange
- **EconomicCalendar**: Fetches upcoming economic events that may impact markets
- **VolatilityAnalyzer**: Calculates various volatility metrics from market data
- **TradingRecommendation**: Applies rules to generate trading advice
- **GoogleSheetsManager**: Updates spreadsheets with trading data and recommendations
- **EmailNotifier**: Sends formatted HTML reports to subscribers

## Trading Recommendation Rules

The system applies the following rules to determine appropriate trading actions:

| Volatility Score | Event Impact | Recommendation          | Risk Level          |
|------------------|--------------|-------------------------|---------------------|
| > 0.8            | > 0.7        | HOLD                    | Extreme             |
| > 0.8            | ≤ 0.7        | SCALP ONLY              | Very High           |
| > 0.6            | > 0.6        | REDUCE EXPOSURE         | High                |
| > 0.6            | ≤ 0.6        | TRADE WITH CAUTION      | Elevated            |
| > 0.4            | > 0.5        | SELECTIVE TRADING       | Moderate            |
| > 0.4            | ≤ 0.5        | TRADE NORMALLY          | Normal              |
| > 0.2            | > 0.6        | PREPARE FOR VOLATILITY  | Low but increasing  |
| > 0.2            | ≤ 0.6        | LONGER TIMEFRAMES       | Low                 |
| ≤ 0.2            | > 0.5        | PREPARE FOR BREAKOUTS   | Very Low but watch  |
| ≤ 0.2            | ≤ 0.5        | RANGE TRADING           | Very Low            |

## Configuration

Edit `config.py` to adjust:
- Trading pairs to monitor
- Volatility calculation parameters
- Trading recommendation rules
- Scheduling options

## Maintenance Schedule

- **Daily**: Automatic data collection and report generation (8:00 UTC)
- **Weekly**: Code updates and algorithm improvements
- **Monthly**: API token renewal and performance review
- **Quarterly**: Full system review and enhancement planning

## License

MIT