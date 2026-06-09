import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading

from ia import perguntar_ia
from banco import inicializar_banco, salvar_pergunta, listar_historico, limpar_historico
from audio import falar

COR_BG       = "#1e1e2e"
COR_PAINEL   = "#2a2a3d"
COR_ENTRADA  = "#313145"
COR_PRIMARIA = "#7c6af7"
COR_HOVER    = "#9b8fff"
COR_TEXTO    = "#cdd6f4"
COR_SUTIL    = "#a0a8c0"
COR_SUCESSO  = "#a6e3a1"
COR_ERRO     = "#f38ba8"
COR_AVISO    = "#f9e2af"

FONTE_TITULO  = ("Helvetica", 14, "bold")
FONTE_NORMAL  = ("Helvetica", 11)
FONTE_PEQUENA = ("Helvetica", 9)
FONTE_MONO    = ("Courier", 11)

banco_ok = False

def criar_botao(parent, texto, comando, cor=COR_PRIMARIA, largura=140):
    frame = tk.Frame(parent, bg=cor, cursor="hand2")
    label = tk.Label(frame, text=texto, bg=cor, fg="white",
                     font=FONTE_NORMAL, padx=12, pady=7, width=largura//10)
    label.pack()
    frame.bind("<Button-1>", lambda e: comando())
    label.bind("<Button-1>", lambda e: comando())
    frame.bind("<Enter>", lambda e: (frame.config(bg=COR_HOVER), label.config(bg=COR_HOVER)))
    frame.bind("<Leave>", lambda e: (frame.config(bg=cor), label.config(bg=cor)))
    label.bind("<Enter>", lambda e: (frame.config(bg=COR_HOVER), label.config(bg=COR_HOVER)))
    label.bind("<Leave>", lambda e: (frame.config(bg=cor), label.config(bg=cor)))
    return frame


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Assistente de Estudos IA")
        self.root.geometry("820x620")
        self.root.configure(bg=COR_BG)
        self.root.resizable(True, True)
        self._construir_interface()
        self._verificar_banco()

    def _construir_interface(self):
        header = tk.Frame(self.root, bg=COR_PAINEL, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Assistente de Estudos com IA",
                 font=FONTE_TITULO, bg=COR_PAINEL, fg=COR_TEXTO).pack()
        tk.Label(header, text="Powered by Groq",
                 font=FONTE_PEQUENA, bg=COR_PAINEL, fg=COR_SUTIL).pack()

        self.status_var = tk.StringVar(value="Iniciando...")
        self.status_label = tk.Label(self.root, textvariable=self.status_var,
                                     font=FONTE_PEQUENA, bg=COR_BG, fg=COR_SUTIL, anchor="w", padx=12)
        self.status_label.pack(fill="x")

        frame_saida = tk.Frame(self.root, bg=COR_BG, padx=14, pady=6)
        frame_saida.pack(fill="both", expand=True)
        tk.Label(frame_saida, text="Resposta:", font=FONTE_PEQUENA,
                 bg=COR_BG, fg=COR_SUTIL).pack(anchor="w")
        self.saida = scrolledtext.ScrolledText(
            frame_saida, font=FONTE_MONO, bg=COR_ENTRADA, fg=COR_TEXTO,
            insertbackground=COR_TEXTO, relief="flat", wrap="word",
            selectbackground=COR_PRIMARIA, padx=10, pady=8
        )
        self.saida.pack(fill="both", expand=True)
        self.saida.config(state="disabled")

        frame_entrada = tk.Frame(self.root, bg=COR_PAINEL, padx=14, pady=10)
        frame_entrada.pack(fill="x")
        tk.Label(frame_entrada, text="Sua duvida:",
                 font=FONTE_PEQUENA, bg=COR_PAINEL, fg=COR_SUTIL).grid(row=0, column=0, sticky="w")
        self.entrada = tk.Entry(frame_entrada, font=FONTE_NORMAL, bg=COR_ENTRADA, fg=COR_TEXTO,
                                insertbackground=COR_TEXTO, relief="flat", bd=0)
        self.entrada.grid(row=1, column=0, sticky="ew", ipady=8, padx=(0, 10))
        self.entrada.bind("<Return>", lambda e: self.enviar_pergunta())
        frame_entrada.columnconfigure(0, weight=1)

        frame_botoes = tk.Frame(frame_entrada, bg=COR_PAINEL)
        frame_botoes.grid(row=1, column=1)
        criar_botao(frame_botoes, "Perguntar", self.enviar_pergunta, COR_PRIMARIA, 130).pack(side="left", padx=2)
        criar_botao(frame_botoes, "Ouvir", self.ouvir_resposta, "#5a5a7a", 90).pack(side="left", padx=2)

        frame_rodape = tk.Frame(self.root, bg=COR_BG, padx=14, pady=8)
        frame_rodape.pack(fill="x")
        criar_botao(frame_rodape, "Ver historico", self.mostrar_historico, "#5a5a7a", 150).pack(side="left", padx=2)
        criar_botao(frame_rodape, "Limpar historico", self.limpar_hist, "#c0394a", 150).pack(side="left", padx=2)
        criar_botao(frame_rodape, "Limpar tela", self.limpar_tela, "#5a5a7a", 130).pack(side="left", padx=2)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")

    def _verificar_banco(self):
        global banco_ok
        ok, erro = inicializar_banco()
        banco_ok = ok
        if ok:
            self._set_status("Banco conectado. Pronto para usar!", COR_SUCESSO)
        else:
            self._set_status(f"Banco indisponivel: {erro[:60]}", COR_AVISO)

    def _set_status(self, msg, cor=COR_SUTIL):
        self.status_var.set(msg)
        self.status_label.config(fg=cor)

    def _escrever(self, texto, cor=None):
        self.saida.config(state="normal")
        if cor:
            tag = f"cor_{cor.replace('#','')}"
            self.saida.tag_config(tag, foreground=cor)
            self.saida.insert("end", texto, tag)
        else:
            self.saida.insert("end", texto)
        self.saida.see("end")
        self.saida.config(state="disabled")

    def _limpar_saida(self):
        self.saida.config(state="normal")
        self.saida.delete("1.0", "end")
        self.saida.config(state="disabled")

    def enviar_pergunta(self):
        pergunta = self.entrada.get().strip()
        if not pergunta:
            return
        self.entrada.delete(0, "end")
        self._limpar_saida()
        self._escrever(f"Pergunta: {pergunta}\n\n", COR_PRIMARIA)
        self._set_status("Consultando a IA...", COR_AVISO)
        self.progress.pack(fill="x", padx=14, pady=2)
        self.progress.start(10)
        threading.Thread(target=lambda: self.root.after(0, lambda: self._exibir_resposta(pergunta, perguntar_ia(pergunta))), daemon=True).start()

    def _exibir_resposta(self, pergunta, resposta):
        self.progress.stop()
        self.progress.pack_forget()
        if resposta.startswith("❌") or resposta.startswith("⚠️"):
            self._escrever(resposta + "\n", COR_ERRO)
            self._set_status("Erro ao consultar a IA.", COR_ERRO)
        else:
            self._escrever(resposta + "\n", COR_TEXTO)
            self._set_status("Resposta recebida.", COR_SUCESSO)
            if banco_ok:
                salvar_pergunta(pergunta, resposta)

    def ouvir_resposta(self):
        texto = self.saida.get("1.0", "end").strip()
        if texto:
            falar(texto)
            self._set_status("Reproduzindo audio...", COR_SUTIL)

    def mostrar_historico(self):
        dados = listar_historico()
        self._limpar_saida()
        if dados is None:
            self._escrever("Banco de dados indisponivel.\n", COR_AVISO)
            return
        if not dados:
            self._escrever("Nenhuma pergunta no historico ainda.\n", COR_SUTIL)
            return
        self._escrever(f"Ultimas {len(dados)} perguntas:\n\n", COR_PRIMARIA)
        for pergunta, resposta, criado_em in dados:
            data_str = criado_em.strftime("%d/%m/%Y %H:%M") if criado_em else ""
            self._escrever(f"{data_str}\n", COR_SUTIL)
            self._escrever(f"Pergunta: {pergunta}\n", COR_AVISO)
            self._escrever(f"{resposta}\n", COR_TEXTO)
            self._escrever("-" * 60 + "\n", COR_SUTIL)
        self._set_status(f"Historico carregado ({len(dados)} itens).", COR_SUCESSO)

    def limpar_hist(self):
        if messagebox.askyesno("Confirmar", "Deseja apagar todo o historico?"):
            if limpar_historico():
                self._set_status("Historico apagado.", COR_SUTIL)
            else:
                self._set_status("Erro ao apagar historico.", COR_ERRO)

    def limpar_tela(self):
        self._limpar_saida()
        self._set_status("Tela limpa.", COR_SUTIL)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
