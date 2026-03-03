from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/next-race")
def get_next_race(db: Session = Depends(get_db)):
    query = text("""
        SELECT nome_gp, circuito, data_corrida, hora_corrida 
        FROM calendario_f1 
        WHERE data_corrida >= CURRENT_DATE 
        ORDER BY data_corrida ASC 
        LIMIT 1
    """)
    result = db.execute(query).fetchone()
    
    if result:
        return {
            "nome_gp": result[0],
            "circuito": result[1],
            "data_corrida": str(result[2]),
            "hora_corrida": str(result[3])
        }
    return {"message": "Nenhuma corrida futura encontrada"}

@app.get("/api/results/{gp_id}")
def get_results(gp_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT posicao, piloto_nome, construtor_id, pontos, tempo_total, status_resultado
        FROM resultados_gp 
        WHERE gp_id = :gp_id 
        ORDER BY posicao ASC
    """)
    results = db.execute(query, {"gp_id": gp_id}).fetchall()
    return results