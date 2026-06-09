import os
import sys
import threading
from gtts import gTTS

def falar(texto: str):
    """Converte texto em áudio e reproduz. Funciona em Windows, Mac e Linux."""
    if not texto.strip():
        return

    def _reproduzir():
        try:
            tts = gTTS(text=texto[:500], lang='pt')  # limita tamanho para não demorar
            caminho = "resposta.mp3"
            tts.save(caminho)

            # Comando compatível com cada sistema operacional
            if sys.platform == "win32":
                os.system(f'start "" "{caminho}"')
            elif sys.platform == "darwin":  # macOS
                os.system(f'afplay "{caminho}"')
            else:  # Linux
                os.system(f'mpg123 "{caminho}" 2>/dev/null || ffplay -nodisp -autoexit "{caminho}" 2>/dev/null')

        except Exception as e:
            print(f"Erro no áudio: {e}")

    # Executa em thread separada para não travar a interface
    threading.Thread(target=_reproduzir, daemon=True).start()
