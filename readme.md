 # SangOdds - Sports Arbitrage Opportunity Finder

A Python application that fetches real-time sports betting odds from multiple bookmakers and identifies arbitrage opportunities across NBA, MLB, NFL, and NHL games.

## 📋 Features

- **Multi-Sport Support**: Fetches odds for NBA, MLB, NFL, and NHL games
- **Arbitrage Detection**: Automatically identifies guaranteed profit opportunities by comparing odds across different bookmakers
- **Live/Upcoming Status**: Displays whether games are currently live or upcoming
- **EST Time Display**: All game times are converted to Eastern Time (EST/EDT) for easy reference
- **Optimal Betting Strategy**: Calculates the optimal bet distribution to maximize guaranteed profit
- **Profit Margin Analysis**: Shows profit margins and guaranteed profit amounts
- **Organized Display**: Results are organized by sport with clear formatting

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository:
```bash
git clone <repository-url>
cd SangOdds
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 📦 Requirements

The project requires the following Python packages:

- `requests` - For making HTTP requests to the odds API
- `pytz` - For timezone conversion (UTC to EST)

## 🎯 Usage

### Basic Usage

Run the main script to fetch odds and find arbitrage opportunities:

```bash
python main.py
```

The script will:
1. Fetch odds for all configured sports (NBA, MLB, NFL, NHL)
2. Analyze each game for arbitrage opportunities
3. Display results organized by sport

### Programmatic Usage

You can also import and use the classes in your own code:

```python
from get_odds.get_odds import GetOdds

# Get games for specific sports
sports = ["basketball_nba", "baseball_mlb"]
games_by_sport = GetOdds.get_games(sports)

# Find arbitrage opportunities for a specific sport
for sport_key, games in games_by_sport.items():
    opportunities = GetOdds.find_arbitrage_opportunities(games)
    GetOdds.display_arbitrage_opportunities({sport_key: opportunities})
```

## 📁 Project Structure

```
SangOdds/
├── get_odds/
│   ├── __init__.py
│   └── get_odds.py          # Main odds fetching and arbitrage detection logic
├── helpers/
│   ├── __init__.py
│   └── helpers.py           # Utility functions (time conversion, probability calculations)
├── main.py                  # Entry point script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 How It Works

### Arbitrage Detection Algorithm

1. **Odds Fetching**: The script fetches odds from multiple bookmakers via The Odds API
2. **Best Odds Finding**: For each game, it identifies the best odds for home and away teams from different bookmakers
3. **Probability Calculation**: Converts decimal odds to implied probabilities
4. **Arbitrage Identification**: Checks if the sum of implied probabilities is less than 1.0 (indicating an arbitrage opportunity)
5. **Optimal Betting**: Calculates the optimal bet distribution to guarantee profit regardless of outcome
6. **Profit Calculation**: Determines the guaranteed profit margin

### Time Conversion

- Game times from the API are in UTC format
- The script converts all times to Eastern Time (EST/EDT) using the `pytz` library
- Games are marked as "LIVE" if they've started within the last 4 hours (configurable)

### Live Game Detection

Games are considered "LIVE" if:
- The current time is after the game's commence time
- The game started within the last 4 hours (default duration)

Games are marked as "UPCOMING" if they haven't started yet.

## 📊 Example Output

```
Fetching odds for all sports...
Sports: NBA, MLB, NFL, NHL

Found 10 NBA game(s). Analyzing for arbitrage opportunities...
Found 15 MLB game(s). Analyzing for arbitrage opportunities...
Found 5 NFL game(s). Analyzing for arbitrage opportunities...
Found 12 NHL game(s). Analyzing for arbitrage opportunities...

ARBITRAGE OPPORTUNITIES BY SPORT

====================================================================================================
NBA - 2 Opportunity(ies)
====================================================================================================

Opportunity #1 [⏰ UPCOMING]
  Game: Lakers @ Warriors
  Time: 2024-01-15 08:00 PM EST
  Home Team (Warriors): 2.150 @ DraftKings
  Away Team (Lakers): 1.950 @ FanDuel
  Total Implied Probability: 0.9875
  Profit Margin: 1.25%
  Optimal Bet Distribution (for $100 stake):
    - Bet $48.70 on Warriors @ DraftKings
    - Bet $51.30 on Lakers @ FanDuel
  Guaranteed Profit: $1.25
----------------------------------------------------------------------------------------------------
```

## ⚙️ Configuration

### Supported Sports

The default sports are:
- `basketball_nba` - NBA
- `baseball_mlb` - MLB
- `americanfootball_nfl` - NFL
- `icehockey_nhl` - NHL

You can modify the sports list in `main.py`:

```python
sports = ["basketball_nba", "baseball_mlb"]  # Only fetch NBA and MLB
```

### API Configuration

The API key is stored in `get_odds/get_odds.py`. You can update it if needed:

```python
class GetOdds:
    key = "your-api-key-here"
    base_url = "https://api.the-odds-api.com/v4/sports"
```

## 📝 Key Classes and Methods

### `GetOdds` Class

- `get_games(sports, regions, markets, odds_format)` - Fetches odds for specified sports
- `find_arbitrage_opportunities(games)` - Identifies arbitrage opportunities from game data
- `display_arbitrage_opportunities(opportunities_by_sport)` - Displays results in a formatted way

### `HelperManager` Class

- `decimal_to_probability(decimal_odds)` - Converts decimal odds to implied probability
- `convert_to_est(utc_time_str)` - Converts UTC time to EST with formatted string
- `is_game_live(commence_time_str, max_game_duration_hours)` - Determines if a game is currently live

## ⚠️ Important Notes

1. **API Key**: This project uses The Odds API. Make sure you have a valid API key with sufficient requests available.

2. **Rate Limits**: Be mindful of API rate limits. The Odds API has request limits based on your subscription plan.

3. **Arbitrage Opportunities**: Real arbitrage opportunities are rare and typically have small profit margins. This tool is for educational purposes.

4. **Betting Disclaimer**: This software is for informational and educational purposes only. Always gamble responsibly and within your means. Be aware of:
   - Bookmaker terms and conditions
   - Account restrictions
   - Potential for odds to change before placing bets
   - Regional gambling laws and regulations

5. **Time Sensitivity**: Odds change rapidly. An arbitrage opportunity identified now may not be available moments later.

6. **Minimum Bookmakers**: The script requires at least 2 bookmakers per game to detect arbitrage opportunities.

## 🔍 How Arbitrage Works

Arbitrage occurs when the sum of implied probabilities across different bookmakers is less than 100%. This means you can bet on all possible outcomes and guarantee a profit.

**Example:**
- Bookmaker A: Team 1 wins at odds of 2.10 (implied probability: 47.6%)
- Bookmaker B: Team 2 wins at odds of 2.10 (implied probability: 47.6%)
- Total implied probability: 95.2%
- Arbitrage opportunity: 4.8% profit margin

By betting optimally on both outcomes, you guarantee a profit regardless of which team wins.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is for educational purposes. Please ensure compliance with:
- The Odds API terms of service
- Local gambling laws and regulations
- Bookmaker terms and conditions

## 🆘 Troubleshooting

### Import Errors

If you encounter import errors, make sure:
- All dependencies are installed: `pip install -r requirements.txt`
- You're running Python 3.8 or higher
- The package structure is intact (check for `__init__.py` files)

### API Errors

If you see API errors:
- Verify your API key is correct
- Check your API request quota/limits
- Ensure you have an internet connection
- Check if The Odds API service is operational

### No Opportunities Found

This is normal! Arbitrage opportunities are rare. The script will display "No arbitrage opportunities found" when none are detected.

## 📞 Support

For issues or questions:
- Check The Odds API documentation: https://the-odds-api.com/
- Review the code comments for detailed explanations
- Ensure all requirements are properly installed

---

**Remember**: Always gamble responsibly and within your legal jurisdiction.

