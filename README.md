# SangOdds - Sports Arbitrage Finder

A PySide6 desktop app that fetches real-time sports betting odds from multiple bookmakers and surfaces arbitrage opportunities across NBA, MLB, NFL, and NHL.

## Features

- **GUI** — dark-themed PySide6 interface, results update without freezing the window
- **Multi-sport** — NBA, MLB, NFL, NHL with per-sport toggles
- **Live detection** — games are flagged LIVE vs UPCOMING
- **Arbitrage engine** — finds opportunities where total implied probability < 1
- **Custom stake** — change your stake and the table recalculates instantly
- **EST times** — all game times converted from UTC to Eastern

## Setup

**Prerequisites:** Python 3.10+

1. Clone the repo:
   ```bash
   git clone https://github.com/SANGQR/SangOdds.git
   cd SangOdds
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. Add your API key — copy `.env.example` to `.env` and fill it in:
   ```bash
   cp .env.example .env
   ```
   ```
   ODDS_API_KEY=your_key_here
   ```
   Get a free key at [the-odds-api.com](https://the-odds-api.com/).

## Usage

```bash
python main.py
```

Select the sports you want, set your total stake, and click **Fetch Odds**. Arbitrage opportunities are listed in the table with profit margin and optimal bet splits highlighted in green.

## Project Structure

```
SangOdds/
├── main.py              # Entry point — launches the GUI
├── gui.py               # PySide6 window and fetch worker thread
├── get_odds/
│   └── get_odds.py      # Odds API client and arbitrage detection
├── helpers/
│   └── helpers.py       # Time conversion and probability utilities
├── .env.example         # Environment variable template
├── requirements.txt
└── .gitignore
```

## How Arbitrage Works

Arbitrage exists when the sum of implied probabilities across bookmakers is below 100%, meaning you can cover every outcome and guarantee a profit.

| Bookmaker | Team | Odds | Implied Prob |
|-----------|------|------|-------------|
| DraftKings | Team A | 2.10 | 47.6% |
| FanDuel | Team B | 2.10 | 47.6% |
| **Total** | | | **95.2%** → 4.8% edge |

The app calculates the exact stake split for your chosen total so the payout is the same regardless of result.

## Disclaimer

For informational and educational purposes only. Odds change rapidly; verify before placing any bets. Gamble responsibly and within your local laws.
