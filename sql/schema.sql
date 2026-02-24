CREATE TABLE calendario_f1 (
    id SERIAL PRIMARY KEY,
    temporada INT,
    ROUND INT,
    nome_gp VARCHAR(255) NOT NULL,
    circuito VARCHAR(255) NOT NULL,
    data_corrida DATE NOT NULL,
    horario TIME NOT NULL,
    localidade VARCHAR(50) NOT NULL,
    pais VARCHAR(50) NOT NULL,
    STATUS VARCHAR(20) DEFAULT 'Agendado',
)

CREATE TABLE resultados_gp (
    id SERIAL PRIMARY KEY,
    gp_id INT REFERENCES calendario_f1(id),
    posicao INT,
    numero_carro INT,
    piloto_nome VARCHAR(100),
    piloto_id VARCHAR(50),
    construtor_id VARCHAR(50),
    pontos FLOAT,
    grid_largada INT,
    tempo_total VARCHAR(50),
    melhor_volta_tempo VARCHAR(50),
    rank_melhor_volta INT,
    status_resultado VARCHAR(50)
);