import tkinter as tk
from tkinter import scrolledtext
from ia import perguntar_ia
from banco import salvar_pergunta, listar_historico
from audio import falar

def enviar_pergunta():
    pergunta = entrada.get()

    if not pergunta.strip():
        return

    resposta = perguntar_ia(pergunta)
    salvar_pergunta(pergunta, resposta)

    saida.delete("1.0", tk.END)
    saida.insert(tk.END, resposta)

def ouvir():
    texto = saida.get("1.0", tk.END)
    falar(texto)

def mostrar_historico():
    historico = listar_historico()
    saida.delete("1.0", tk.END)

    for p, r in historico:
        saida.insert(tk.END, f"P: {p}\nR: {r}\n\n")

janela = tk.Tk()
janela.title("Assistente IA")
janela.geometry("700x500")

tk.Label(janela, text="Digite sua dúvida:").pack()

entrada = tk.Entry(janela, width=80)
entrada.pack(pady=10)

tk.Button(janela, text="Perguntar", command=enviar_pergunta).pack()
tk.Button(janela, text="Ouvir resposta", command=ouvir).pack()
tk.Button(janela, text="Histórico", command=mostrar_historico).pack()

saida = scrolledtext.ScrolledText(janela, width=80, height=20)
saida.pack(pady=10)

janela.mainloop()