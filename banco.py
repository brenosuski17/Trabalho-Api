import psycopg2
from config import DB_CONFIG

_conn_cache = None

def conectar():
    """Retorna uma conexão com o banco de dados."""
    return psycopg2.connect(**DB_CONFIG)

def inicializar_banco():
    """Cria a tabela se não existir. Retorna (True, '') ou (False, mensagem_erro)."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS perguntas (
                id        SERIAL PRIMARY KEY,
                pergunta  TEXT NOT NULL,
                resposta  TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True, ""
    except psycopg2.OperationalError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def salvar_pergunta(pergunta: str, resposta: str) -> bool:
    """Salva uma pergunta e resposta. Retorna True se salvou com sucesso."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO perguntas (pergunta, resposta) VALUES (%s, %s)",
            (pergunta, resposta)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False

def listar_historico(limite: int = 20):
    """Lista as últimas perguntas e respostas. Retorna lista ou None se erro."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pergunta, resposta, criado_em FROM perguntas ORDER BY id DESC LIMIT %s",
            (limite,)
        )
        dados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dados
    except Exception:
        return None

def limpar_historico() -> bool:
    """Remove todo o histórico. Retorna True se sucesso."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM perguntas")
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False
