import psycopg2
from config import DB_CONFIG

def conectar():
    return psycopg2.connect(**DB_CONFIG)

def salvar_pergunta(pergunta, resposta):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO perguntas (pergunta, resposta) VALUES (%s, %s)",
        (pergunta, resposta)
    )

    conn.commit()
    cursor.close()
    conn.close()

def listar_historico():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT pergunta, resposta FROM perguntas ORDER BY id DESC")
    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados