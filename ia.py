from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def perguntar_ia(texto: str) -> str:
    if not os.getenv("GROQ_API_KEY"):
        return "⚠️ API Key não configurada. Verifique o arquivo .env"

    try:
        resposta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Você é um assistente de estudos. Responda de forma clara e didática em português."},
                {"role": "user", "content": texto}
            ]
        )
        return resposta.choices[0].message.content

    except Exception as e:
        erro = str(e)
        if "401" in erro:
            return "❌ API Key inválida. Verifique o arquivo .env"
        elif "429" in erro:
            return "⏳ Limite de uso atingido. Aguarde e tente novamente."
        else:
            return f"❌ Erro ao consultar a IA: {erro}"
