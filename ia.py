import google.generativeai as genai
from config import API_KEY

# Configura a API
genai.configure(api_key=API_KEY)

# Modelo atual e compatível
model = genai.GenerativeModel("gemini-1.5-flash")

# Histórico de conversa para contexto
_historico = []

def perguntar_ia(texto: str) -> str:
    """Envia uma pergunta para o Gemini e retorna a resposta."""
    if not API_KEY:
        return "⚠️ API Key não configurada. Verifique o arquivo .env"

    try:
        # Adiciona contexto de assistente de estudos
        prompt = f"Você é um assistente de estudos. Responda de forma clara e didática em português.\n\nPergunta: {texto}"
        resposta = model.generate_content(prompt)
        return resposta.text

    except Exception as e:
        erro = str(e)
        if "API_KEY" in erro or "authentication" in erro.lower():
            return "❌ Erro de autenticação: verifique sua GEMINI_API_KEY no arquivo .env"
        elif "quota" in erro.lower() or "429" in erro:
            return "⏳ Limite de uso da API atingido. Aguarde alguns segundos e tente novamente."
        else:
            return f"❌ Erro ao consultar a IA: {erro}"
