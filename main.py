import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading

from ia import perguntar_ia
from banco import inicializar_banco, salvar_pergunta, listar_historico, limpar_historico
from audio import falar

# ── Paleta de cores ──────────────────────────────────────────────
COR_BG        = "#1e1e2e"   # fundo escuro
COR_PAINEL    = "#2a2a3d"   # painéis internos
COR_ENTRADA   = "#313145"   # campo de texto
COR_PRIMARIA  = "#7c6af7"   # roxo principal
COR_HOVER     = "#9b8fff"   # hover dos botões
COR_TEXTO     = "#cdd6f4"   # texto principal
COR_SUTIL     = "#6c7086"   # texto secundário
COR_SUCESSO   = "#a6e3a1"   # verde
COR_ERRO      = "#f38ba8"   # vermelho
COR_AVISO     = "#f9e2af"   # amarelo

FONTE_TITULO  = ("Segoe UI", 14, "bold")
FONTE_NORMAL  = ("Segoe UI", 10)
FONTE_PEQUENA = ("Segoe UI", 9)
FONTE_MONO    = ("Consolas", 10)

banco_ok = False  # status da conexão com o banco


def criar_botao(parent, texto, comando, cor=COR_PRIMARIA, largura=18):
    btn = tk.Button(
        parent, text=texto, command=comando,
        bg=cor, fg="white", font=FONTE_NORMAL,
        relief="flat", cursor="hand2", width=largura,
        padx=8, pady=6, bd=0
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=COR_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor))
    return btn


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Assistente de Estudos IA")
        self.root.geometry("820x620")
        self.root.configure(bg=COR_BG)
        self.root.resizable(True, True)

        self._construir_interface()
        self._verificar_banco()

    # ── Construção da interface ──────────────────────────────────
    def _construir_interface(self):
        # Cabeçalho
        header = tk.Frame(self.root, bg=COR_PAINEL, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="🎓 Assistente de Estudos com IA",
                 font=FONTE_TITULO, bg=COR_PAINEL, fg=COR_TEXTO).pack()
        tk.Label(header, text="Powered by Google Gemini",
                 font=FONTE_PEQUENA, bg=COR_PAINEL, fg=COR_SUTIL).pack()

        # Status bar
        self.status_var = tk.StringVar(value="⚡ Iniciando...")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              font=FONTE_PEQUENA, bg=COR_BG, fg=COR_SUTIL, anchor="w", padx=12)
        status_bar.pack(fill="x")

        # Área de resposta
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

        # Área de entrada
        frame_entrada = tk.Frame(self.root, bg=COR_PAINEL, padx=14, pady=10)
        frame_entrada.pack(fill="x")

        tk.Label(frame_entrada, text="Sua dúvida:",
                 font=FONTE_PEQUENA, bg=COR_PAINEL, fg=COR_SUTIL).grid(row=0, column=0, sticky="w")

        self.entrada = tk.Entry(
            frame_entrada, font=FONTE_NORMAL, bg=COR_ENTRADA, fg=COR_TEXTO,
            insertbackground=COR_TEXTO, relief="flat", bd=0
        )
        self.entrada.grid(row=1, column=0, sticky="ew", ipady=8, padx=(0, 10))
        self.entrada.bind("<Return>", lambda e: self.enviar_pergunta())
        frame_entrada.columnconfigure(0, weight=1)

        # Botões
        frame_botoes = tk.Frame(frame_entrada, bg=COR_PAINEL)
        frame_botoes.grid(row=1, column=1)

        criar_botao(frame_botoes, "📤 Perguntar", self.enviar_pergunta, largura=14).pack(side="left", padx=2)
        criar_botao(frame_botoes, "🔊 Ouvir", self.ouvir_resposta, COR_SUTIL, largura=10).pack(side="left", padx=2)

        # Rodapé com botões secundários
        frame_rodape = tk.Frame(self.root, bg=COR_BG, padx=14, pady=8)
        frame_rodape.pack(fill="x")

        criar_botao(frame_rodape, "📋 Ver histórico", self.mostrar_historico, COR_PAINEL, 16).pack(side="left", padx=2)
        criar_botao(frame_rodape, "🗑 Limpar histórico", self.limpar_hist, "#e05555", 16).pack(side="left", padx=2)
        criar_botao(frame_rodape, "🧹 Limpar tela", self.limpar_tela, COR_PAINEL, 14).pack(side="left", padx=2)

        # Barra de progresso (escondida)
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")

    # ── Lógica ──────────────────────────────────────────────────
    def _verificar_banco(self):
        global banco_ok
        ok, erro = inicializar_banco()
        banco_ok = ok
        if ok:
            self._set_status("✅ Banco conectado. Pronto para usar!", COR_SUCESSO)
        else:
            self._set_status(f"⚠️ Banco indisponível (histórico desativado): {erro[:60]}", COR_AVISO)

    def _set_status(self, msg, cor=COR_SUTIL):
        self.status_var.set(msg)
        # Localiza o label de status e atualiza cor
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("textvariable") == str(self.status_var):
                widget.config(fg=cor)
                break

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
        self._escrever(f"❓ {pergunta}\n\n", COR_PRIMARIA)
        self._set_status("🤔 Consultando a IA...", COR_AVISO)
        self.progress.pack(fill="x", padx=14, pady=2)
        self.progress.start(10)

        def _chamar_ia():
            resposta = perguntar_ia(pergunta)
            self.root.after(0, lambda: self._exibir_resposta(pergunta, resposta))

        threading.Thread(target=_chamar_ia, daemon=True).start()

    def _exibir_resposta(self, pergunta, resposta):
        self.progress.stop()
        self.progress.pack_forget()

        if resposta.startswith("❌") or resposta.startswith("⚠️"):
            self._escrever(resposta + "\n", COR_ERRO)
            self._set_status("Erro ao consultar a IA.", COR_ERRO)
        else:
            self._escrever(resposta + "\n", COR_TEXTO)
            self._set_status("✅ Resposta recebida.", COR_SUCESSO)

            if banco_ok:
                salvar_pergunta(pergunta, resposta)

    def ouvir_resposta(self):
        texto = self.saida.get("1.0", "end").strip()
        if texto:
            falar(texto)
            self._set_status("🔊 Reproduzindo áudio...", COR_SUTIL)

    def mostrar_historico(self):
        dados = listar_historico()
        self._limpar_saida()

        if dados is None:
            self._escrever("⚠️ Banco de dados indisponível.\n", COR_AVISO)
            return
        if not dados:
            self._escrever("Nenhuma pergunta no histórico ainda.\n", COR_SUTIL)
            return

        self._escrever(f"📋 Últimas {len(dados)} perguntas:\n\n", COR_PRIMARIA)
        for pergunta, resposta, criado_em in dados:
            data_str = criado_em.strftime("%d/%m/%Y %H:%M") if criado_em else ""
            self._escrever(f"🕐 {data_str}\n", COR_SUTIL)
            self._escrever(f"❓ {pergunta}\n", COR_AVISO)
            self._escrever(f"{resposta}\n", COR_TEXTO)
            self._escrever("─" * 60 + "\n", COR_SUTIL)

        self._set_status(f"📋 Histórico carregado ({len(dados)} itens).", COR_SUCESSO)

    def limpar_hist(self):
        if messagebox.askyesno("Confirmar", "Deseja apagar todo o histórico?"):
            if limpar_historico():
                self._set_status("🗑 Histórico apagado.", COR_SUTIL)
            else:
                self._set_status("⚠️ Erro ao apagar histórico.", COR_ERRO)

    def limpar_tela(self):
        self._limpar_saida()
        self._set_status("Tela limpa.", COR_SUTIL)


# ── Ponto de entrada ────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
