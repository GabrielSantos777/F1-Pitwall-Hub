import requests
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_race_results(year, round_number):
    """
    Busca os resultados de uma corrida específica.
    Exemplo: 2023, Round 1 (Bahrein)
    """

    url = f"{BASE_URL}/{year}/{round_number}/results.json"
    
    try:
        response = requests.get(url)
        data = response.json()

        race_info = data['MRData']['RaceTable']['Races'][0]
        results = race_info['Results']

        print(f"Resultados: {race_info['raceName']} ({year})")
        print(f"{'Pos':<4} | {'Piloto':<20} | {'Tempo/Status':<15} | {'Pontos':<5}")
        print("-" * 50)

        for res in results:
            pos = res['position']
            driver = f"{res['Driver']['givenName']} {res['Driver']['familyName']}"

        # Nem todos os pilotos terminam, então tratamos o tempo/status
            time_or_status = res.get('Time', {}).get('time', res['status'])
            points = res['points']
            
            print(f"{pos:<4} | {driver:<20} | {time_or_status:<15} | {points:<5}")
        
        return results
    except Exception as e:
        print(f"Erro ao buscar resultados: {e}")
        return None
if __name__ == "__main__":
    fetch_race_results(2023, 20)