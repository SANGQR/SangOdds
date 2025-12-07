import requests
from typing import List, Dict
from helpers.helpers import HelperManager

class GetOdds:
    key = "" # Add your own API key from the-odds-api.com
    base_url = "https://api.the-odds-api.com/v4/sports"
    
    # Sport name mappings for display
    SPORT_NAMES = {
        "basketball_nba": "NBA",
        "baseball_mlb": "MLB",
        "americanfootball_nfl": "NFL",
        "icehockey_nhl": "NHL"
    }
    
    @classmethod
    def get_games(cls, sports: List[str] = ["basketball_nba", "baseball_mlb", "americanfootball_nfl", "icehockey_nhl"], 
                  regions: str = "us", markets: str = "h2h,spreads,totals", 
                  odds_format: str = "decimal") -> Dict[str, List[Dict]]:
        """
        Get odds from the-odds-api.com for multiple sports
        
        Returns:
            Dictionary mapping sport_key to list of games
        """
        all_games_by_sport = {}

        for sport in sports:
            endpoint = f"{cls.base_url}/{sport}/odds"
            params = {
                "apiKey": cls.key,
                "regions": regions,
                "markets": markets,
                "oddsFormat": odds_format
            }
            
            try:
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                games = response.json()
                
                # Add sport_key to each game for easier processing
                for game in games:
                    game["sport_key"] = sport
                
                all_games_by_sport[sport] = games
            except requests.exceptions.RequestException as e:
                print(f"Error fetching odds for {sport}: {e}")
                all_games_by_sport[sport] = []

        return all_games_by_sport

    @classmethod
    def find_arbitrage_opportunities(cls, games: List[Dict]) -> List[Dict]:
        """
        Identify arbitrage opportunities from games
        
        Args:
            games: List of game dictionaries from the API
            
        Returns:
            List of arbitrage opportunities with details
        """
        arbitrage_opportunities = []
        
        for game in games:
            home_team = game.get("home_team", "Unknown")
            away_team = game.get("away_team", "Unknown")
            commence_time = game.get("commence_time", "")
            sport_key = game.get("sport_key", "unknown")
            
            # Convert time to EST
            est_dt, est_time_str = HelperManager.convert_to_est(commence_time)
            is_live = HelperManager.is_game_live(commence_time)
            
            # Get all bookmaker odds
            bookmakers = game.get("bookmakers", [])
            
            if len(bookmakers) < 2:
                continue  # Need at least 2 bookmakers for arbitrage
            
            # Find best odds for each outcome (h2h/moneyline market)
            best_home_odds = None
            best_away_odds = None
            best_home_bookmaker = None
            best_away_bookmaker = None
            
            for bookmaker in bookmakers:
                markets = bookmaker.get("markets", [])
                for market in markets:
                    if market.get("key") == "h2h":  # Moneyline market
                        outcomes = market.get("outcomes", [])
                        for outcome in outcomes:
                            name = outcome.get("name", "")
                            price = outcome.get("price", 0)
                            
                            # Check if this is the best odds for home or away team
                            if name == home_team:
                                if best_home_odds is None or price > best_home_odds:
                                    best_home_odds = price
                                    best_home_bookmaker = bookmaker.get("title", "Unknown")
                            elif name == away_team:
                                if best_away_odds is None or price > best_away_odds:
                                    best_away_odds = price
                                    best_away_bookmaker = bookmaker.get("title", "Unknown")
            
            # Check for arbitrage opportunity
            if best_home_odds and best_away_odds:
                home_prob = HelperManager.decimal_to_probability(best_home_odds)
                away_prob = HelperManager.decimal_to_probability(best_away_odds)
                total_prob = home_prob + away_prob
                
                # Arbitrage exists if total implied probability < 1
                if total_prob < 1.0:
                    profit_margin = (1 - total_prob) * 100
                    
                    # Calculate optimal bet distribution for $100 total stake
                    total_stake = 100
                    home_stake = (home_prob / total_prob) * total_stake
                    away_stake = (away_prob / total_prob) * total_stake
                    
                    # Calculate guaranteed profit
                    home_payout = home_stake * best_home_odds
                    away_payout = away_stake * best_away_odds
                    guaranteed_profit = min(home_payout, away_payout) - total_stake
                    
                    arbitrage_opportunities.append({
                        "sport_key": sport_key,
                        "sport_name": cls.SPORT_NAMES.get(sport_key, sport_key),
                        "game": f"{away_team} @ {home_team}",
                        "home_team": home_team,
                        "away_team": away_team,
                        "commence_time_utc": commence_time,
                        "commence_time_est": est_time_str,
                        "is_live": is_live,
                        "status": "LIVE" if is_live else "UPCOMING",
                        "best_home_odds": round(best_home_odds, 3),
                        "best_away_odds": round(best_away_odds, 3),
                        "home_bookmaker": best_home_bookmaker,
                        "away_bookmaker": best_away_bookmaker,
                        "total_implied_probability": round(total_prob, 4),
                        "profit_margin_percent": round(profit_margin, 2),
                        "optimal_bets": {
                            "home_stake": round(home_stake, 2),
                            "away_stake": round(away_stake, 2),
                            "total_stake": total_stake
                        },
                        "guaranteed_profit": round(guaranteed_profit, 2)
                    })
        
        # Sort by profit margin (highest first)
        arbitrage_opportunities.sort(key=lambda x: x["profit_margin_percent"], reverse=True)
        
        return arbitrage_opportunities
    
    @classmethod
    def display_arbitrage_opportunities(cls, opportunities_by_sport: Dict[str, List[Dict]]):
        """
        Display arbitrage opportunities organized by sport
        """
        print("ARBITRAGE OPPORTUNITIES BY SPORT\n")
        
        total_opportunities = 0
        
        for sport_key, opportunities in opportunities_by_sport.items():
            if not opportunities:
                continue
            
            sport_name = cls.SPORT_NAMES.get(sport_key, sport_key)
            total_opportunities += len(opportunities)
            
            print(f"\n{'=' * 100}")
            print(f"{sport_name} - {len(opportunities)} Opportunity(ies)")
            print(f"{'=' * 100}\n")
            
            for i, opp in enumerate(opportunities, 1):
                
                print(f"Opportunity #{i} [{opp['status']}]")
                print(f"  Game: {opp['game']}")
                print(f"  Time: {opp['commence_time_est']}")
                print(f"  Home Team ({opp['home_team']}): {opp['best_home_odds']} @ {opp['home_bookmaker']}")
                print(f"  Away Team ({opp['away_team']}): {opp['best_away_odds']} @ {opp['away_bookmaker']}")
                print(f"  Total Implied Probability: {opp['total_implied_probability']}")
                print(f"  Profit Margin: {opp['profit_margin_percent']}%")
                print(f"  Optimal Bet Distribution (for $100 stake):")
                print(f"    - Bet ${opp['optimal_bets']['home_stake']:.2f} on {opp['home_team']} @ {opp['home_bookmaker']}")
                print(f"    - Bet ${opp['optimal_bets']['away_stake']:.2f} on {opp['away_team']} @ {opp['away_bookmaker']}")
                print(f"  Guaranteed Profit: ${opp['guaranteed_profit']:.2f}")
                print("-" * 100)
        
        print(f"TOTAL ARBITRAGE OPPORTUNITIES FOUND: {total_opportunities}\n")
        
        if total_opportunities == 0:
            print("No arbitrage opportunities found across all sports.\n")