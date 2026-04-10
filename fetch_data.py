import requests
import json
import time

def fetch_multiple_leagues():
    leagues = {
        "Israel Premier League": 383,
        "English Premier League": 39,
        "Spanish La Liga": 140,
        "Italian Serie A": 135,
        "German Bundesliga": 78,
        "French Ligue 1": 61
    }
    seasons = [2021, 2022, 2023, 2024, 2025]
    headers = {
        'x-apisports-key': 'de4ba3b188c5bb47d1e8aacb8f0ffd90'
    }
    all_data = {}
    print("Starting data fetch... This will take a few minutes because of API speed limits.")
    for league_name, league_id in leagues.items():
        all_data[league_name] = {}
        for season in seasons:
            print(f"Fetching teams for {league_name}, Season {season}...")
            url = f"https://v3.football.api-sports.io/teams?league={league_id}&season={season}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                all_data[league_name][season] = data['response']
            else:
                print(f"Error {response.status_code} fetching {league_name} {season}")
            time.sleep(6.5)
    print("Finished fetching! Saving to file...")
    with open("teams_data.json", "w", encoding="utf-8") as file:
        json.dump(all_data, file, ensure_ascii=False, indent=4)
    print("Success! All data is saved in 'teams_data.json'.")

if __name__ == "__main__":
    fetch_multiple_leagues()