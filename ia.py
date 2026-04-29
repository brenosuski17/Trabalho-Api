import google.generativeai as genai
from config import API_KEY

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def perguntar_ia(texto):
    try:
        resposta = model.generate_content(texto)
        return resposta.text
    except Exception as e:
        return f"Erro na IA: {e}"
    