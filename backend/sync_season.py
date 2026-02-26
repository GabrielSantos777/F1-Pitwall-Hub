import requests
from sqlalchemy import text
from datetime import datetime, date
from database import ENGINE

BASE_URL = "https://api.jolpi.ca/ergast/f1"


def sync_calendar(year):
    print(f"Sincronizando calendário da temporada {year}...")

    url = f"{BASE_URL}/{year}.json"
    response = requests.get(url)

    if response.status_code != 200:
        print("Erro ao buscar dados da API")
        return

    data = response.json()

    races = data["MRData"]["RaceTable"]["Races"]

    with ENGINE.connect() as connection:
        for race in races:
            data_corrida = datetime.strptime(race["date"], "%Y-%m-%d").date()
            status = "Finalizado" if data_corrida <= date.today() else "Agendado"

            upsert_query = text(
                """
                INSERT INTO calendario_f1 (
                    temporada,
                    round,
                    nome_gp,
                    circuito,
                    data_corrida,
                    horario,
                    localidade,
                    pais,
                    status
                )
                VALUES (
                    :temporada,
                    :round,
                    :nome_gp,
                    :circuito,
                    :data_corrida,
                    :horario,
                    :localidade,
                    :pais,
                    :status
                )
                ON CONFLICT (temporada, round)
                DO UPDATE SET
                    nome_gp = EXCLUDED.nome_gp,
                    circuito = EXCLUDED.circuito,
                    data_corrida = EXCLUDED.data_corrida,
                    horario = EXCLUDED.horario,
                    localidade = EXCLUDED.localidade,
                    pais = EXCLUDED.pais,
                    status = EXCLUDED.status
            """
            )

            connection.execute(
                upsert_query,
                {
                    "temporada": year,
                    "round": int(race["round"]),
                    "nome_gp": race["raceName"],
                    "circuito": race["Circuit"]["circuitName"],
                    "data_corrida": data_corrida,
                    "horario": race.get("time", "00:00:00"),
                    "localidade": race["Circuit"]["Location"]["locality"],
                    "pais": race["Circuit"]["Location"]["country"],
                    "status": status,
                },
            )

        connection.commit()

    print(f"Calendário {year} sincronizado com sucesso.")


if __name__ == "__main__":
    year = int(sys.argv[1])
    sync_calendar(year)
    # for year in range(1950, 2026):
    #     sync_calendar(year)
