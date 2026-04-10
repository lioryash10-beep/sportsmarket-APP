import requests
import json

def find_israel_leagues():
    url = "https://v3.football.api-sports.io/leagues?country=Israel"
    
    headers = {
        'x-apisports-key': 'de4ba3b188c5bb47d1e8aacb8f0ffd90'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        print("Leagues in Israel:")
        print("-" * 20)
        for item in data['response']:
            league_id = item['league']['id']
            league_name = item['league']['name']
            print(f"ID: {league_id} | Name: {league_name}")
    else:
        print("Error fetching data")

if __name__ == "__main__":
    find_israel_leagues()