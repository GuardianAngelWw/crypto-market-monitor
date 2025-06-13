# Crypto Market Monitor

A comprehensive tool for monitoring cryptocurrency markets on Bybit, analyzing volatility, tracking economic events, and providing daily trading recommendations.

## Features

- **Economic Calendar Integration**: Fetches and categorizes economic events by impact level (High/Medium/Low)
- **Market Data Analysis**: Collects and processes price, volume, and order book data from Bybit
- **Multi-Factor Volatility Assessment**: Combines Historical Volatility, ATR, Bollinger Bands Width, and Event Impact
- **Trading Recommendations**: Generates actionable trading advice based on market conditions
- **Automated Reporting**: Sends daily email reports and updates Google Sheets for tracking

## Components

- **BybitAPI**: Interface for interacting with the Bybit cryptocurrency exchange
- **EconomicCalendar**: Fetches upcoming economic events that may impact markets
- **VolatilityAnalyzer**: Calculates various volatility metrics from market data
- **TradingRecommendation**: Applies rules to generate trading advice
- **GoogleSheetsManager**: Updates spreadsheets with trading data and recommendations
- **EmailNotifier**: Sends formatted HTML reports to subscribers

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables:
   ```
   BYBIT_API_KEY=your_bybit_api_key
   BYBIT_API_SECRET=your_bybit_api_secret
   GOOGLE_SHEETS_CREDS=your_google_sheets_credentials
   EMAIL_SENDER=your_email_address
   EMAIL_PASSWORD=your_email_password
   EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
   TRADING_ECONOMICS_KEY=your_trading_economics_api_key
   ```
4. Run the script: `python main.py`

## Trading Recommendation Rules

The system applies the following rules to determine appropriate trading actions:

| Volatility Score | Event Impact | Recommendation           | Risk Level          |
|------------------|--------------|--------------------------|---------------------|
| > 0.8            | > 0.7        | HOLD                     | Extreme             |
| > 0.8            | ≤ 0.7        | SCALP ONLY               | Very High           |
| > 0.6            | > 0.6        | REDUCE EXPOSURE          | High                |
| > 0.6            | ≤ 0.6        | TRADE WITH CAUTION       | Elevated            |
| > 0.4            | > 0.5        | SELECTIVE TRADING        | Moderate            |
| > 0.4            | ≤ 0.5        | TRADE NORMALLY           | Normal              |
| > 0.2            | > 0.6        | PREPARE FOR VOLATILITY   | Low but increasing  |
| > 0.2            | ≤ 0.6        | LONGER TIMEFRAMES        | Low                 |
| ≤ 0.2            | > 0.5        | PREPARE FOR BREAKOUTS    | Very Low but watch  |
| ≤ 0.2            | ≤ 0.5        | RANGE TRADING            | Very Low            |

## Maintenance Schedule

- **Daily**: Automatic data collection and report generation (8:00 UTC)
- **Weekly**: Code updates and algorithm improvements
- **Monthly**: API token renewal and performance review
- **Quarterly**: Full system review and enhancement planning

## License

MIT