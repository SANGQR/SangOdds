from get_odds.get_odds import GetOdds
        
def main():
    """Main function to get odds for all sports and identify arbitrage opportunities"""
    sports = ["basketball_nba", "baseball_mlb", "americanfootball_nfl", "icehockey_nhl"]
    
    print("Getting odds...")
    print(f"Sports: {', '.join([GetOdds.SPORT_NAMES.get(s, s) for s in sports])}\n")
    
    all_games_by_sport = GetOdds.get_games(sports)
    
    # Find arbitrage opportunities for each sport
    opportunities_by_sport = {}
    
    for sport_key, games in all_games_by_sport.items():
        if not games:
            print(f"No games found for {GetOdds.SPORT_NAMES.get(sport_key, sport_key)}")
            opportunities_by_sport[sport_key] = []
            continue
        
        print(f"Found {len(games)} {GetOdds.SPORT_NAMES.get(sport_key, sport_key)} game(s).")
        opportunities = GetOdds.find_arbitrage_opportunities(games)
        opportunities_by_sport[sport_key] = opportunities
    
    # Display results
    GetOdds.display_arbitrage_opportunities(opportunities_by_sport)
    
    return opportunities_by_sport


if __name__ == "__main__":
    opportunities = main()