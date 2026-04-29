CREATE TABLE perguntas (
    id SERIAL PRIMARY KEY,
    pergunta TEXT,
    resposta TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);