import requests
from sqlalchemy import text
from database import ENGINE
import sys

BASE_URL = "https://api.jolpi.ca/ergast/f1"


def sync_results(year, round_number):
    print(f"Syncing results for {year} round {round_number}...")

    url = f"{BASE_URL}/{year}/{round_number}/results.json"
    response = requests.get(url)

    if response.status_code != 200:
        print("Erro ao buscar dados da API")
        return

    data = response.json()

    if not data["MRData"]["RaceTable"]["Races"]:
        print(f"Nenhuma corrida encontrada para {year} round {round_number}")
        return

    race_data = data["MRData"]["RaceTable"]["Races"][0]
    results = race_data["Results"]

    with ENGINE.connect() as connection:

        res = connection.execute(
            text("SELECT id FROM calendario_f1 WHERE temporada = :year AND round = :round"),
            {"year": year, "round": round_number},
        ).fetchone()

        gp_id = res[0] if res else None

        if not gp_id:
            print("Calendário não encontrado. Rode sync_calendar primeiro.")
            return

        for result in results:

            upsert_query = text("""
                INSERT INTO resultados_gp (
                    gp_id,
                    posicao,
                    numero_carro,
                    piloto_nome,
                    piloto_id,
                    construtor_id,
                    pontos,
                    grid_largada,
                    tempo_total,
                    melhor_volta_tempo,
                    status_resultado
                )
                VALUES (
                    :gp_id,
                    :posicao,
                    :numero_carro,
                    :piloto_nome,
                    :piloto_id,
                    :construtor_id,
                    :pontos,
                    :grid_largada,
                    :tempo_total,
                    :melhor_volta_tempo,
                    :status_resultado
                )
                ON CONFLICT (gp_id, posicao)
                DO UPDATE SET
                    piloto_nome = EXCLUDED.piloto_nome,
                    construtor_id = EXCLUDED.construtor_id,
                    pontos = EXCLUDED.pontos,
                    grid_largada = EXCLUDED.grid_largada,
                    tempo_total = EXCLUDED.tempo_total,
                    melhor_volta_tempo = EXCLUDED.melhor_volta_tempo,
                    status_resultado = EXCLUDED.status_resultado
            """)

            connection.execute(
                upsert_query,
                {
                    "gp_id": gp_id,
                    "posicao": int(result["position"]),
                    "numero_carro": int(result["number"]),
                    "piloto_nome": f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                    "piloto_id": result["Driver"]["driverId"],
                    "construtor_id": result["Constructor"]["constructorId"],
                    "pontos": float(result["points"]),
                    "grid_largada": int(result["grid"]),
                    "tempo_total": result.get("Time", {}).get("time", "N/A"),
                    "melhor_volta_tempo": result.get("FastestLap", {}).get("Time", {}).get("time", "N/A"),
                    "status_resultado": result["status"],
                },
            )

        connection.commit()

    print(f"Resultados para {year} round {round_number} sincronizados com sucesso.\n")




if __name__ == "__main__":
    year = int(sys.argv[1])
    round_number = int(sys.argv[2])
    sync_results(year, round_number)