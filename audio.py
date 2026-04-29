from gtts import gTTS
import os

def falar(texto):
    tts = gTTS(text=texto, lang='pt')
    tts.save("resposta.mp3")
    os.system("start resposta.mp3")