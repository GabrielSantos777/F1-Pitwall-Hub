import requests
from sqlalchemy import text
from database import ENGINE

BASE_URL = "https://api.jolpi.ca/ergast/f1"


def sync_calendar(year):
    print(f"Syncing calendar for {year}...")

    url = f"{BASE_URL}/{year}.json"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro ao buscar dados do ano {year}")
        return

    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]

    if not races:
        print(f"Nenhuma corrida encontrada para {year}")
        return

    with ENGINE.connect() as connection:
        for race in races:

            upsert_query = text("""
                INSERT INTO calendario_f1 (
                    temporada,
                    round,
                    nome_gp,
                    circuito,
                    data_corrida,
                    horario,
                    localidade,
                    pais
                )
                VALUES (
                    :temporada,
                    :round,
                    :nome_gp,
                    :circuito,
                    :data_corrida,
                    :horario,
                    :localidade,
                    :pais
                )
                ON CONFLICT (temporada, round)
                DO UPDATE SET
                    nome_gp = EXCLUDED.nome_gp,
                    circuito = EXCLUDED.circuito,
                    data_corrida = EXCLUDED.data_corrida,
                    horario = EXCLUDED.horario,
                    localidade = EXCLUDED.localidade,
                    pais = EXCLUDED.pais
            """)

            connection.execute(
                upsert_query,
                {
                    "temporada": int(race["season"]),
                    "round": int(race["round"]),
                    "nome_gp": race["raceName"],
                    "circuito": race["Circuit"]["circuitName"],
                    "data_corrida": race["date"],
                    "horario": race.get("time", "00:00:00Z").replace("Z", ""),
                    "localidade": race["Circuit"]["Location"]["locality"],
                    "pais": race["Circuit"]["Location"]["country"],
                },
            )

        connection.commit()

    print(f"Calendar for {year} synced successfully.\n")


if __name__ == "__main__":
    sync_calendar(2025)
    # for year in range(1950, 2025):