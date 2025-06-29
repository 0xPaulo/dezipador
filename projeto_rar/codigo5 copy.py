# ==========================
# IMPORTS E UTILITÁRIOS
# ==========================
import customtkinter as ctk
from tkinter import filedialog, colorchooser
from pyunpack import Archive
import os
import zipfile
import json
import shutil
import sys
from pathlib import Path


def resource_path(rel_path):
    """Funciona para o .py e também para o .exe"""
    try:
        base_path = sys._MEIPASS  # Quando executado pelo PyInstaller
    except Exception:
        base_path = os.path.abspath(".")  # Quando executado diretamente pelo Python
    return os.path.join(base_path, rel_path)

# ==========================
# CONFIGURAÇÕES E CONSTANTES
# ==========================

# Caminho para a pasta "inuconfig" dentro de "Documentos"
PASTA_CONFIG = Path.home() / "Documents" / "InuSoftware" / "InuZiper" / "InuConfig"
PASTA_CONFIG.mkdir(parents=True, exist_ok=True)  # Cria a pasta se não existir

# Atualiza os caminhos dos arquivos JSON
CAMINHO_JSON = PASTA_CONFIG / "caminhos_zips.json"
CAMINHO_CORES = PASTA_CONFIG / "cores_tema.json"

arquivos_zip = {1: None, 2: None, 3: None}
labels = {}
botao_selecionar = {}
botao_deszipar = {}

fonte_cyber = ("Consolas", 14, "bold")
cores = {
    "fundo_janela": "#1b003b",
    "fundo_frame": "#0a0a23",
    "borda_frame": "#00fff7",
    "texto_label": "#ff3cac",
    "fundo_btn_sel": "#1b003b",
    "hover_btn_sel": "#330066",
    "texto_btn_sel": "#00fff7",
    "borda_btn_sel": "#ff3cac",
    "fundo_btn_deszip": "#330066",
    "hover_btn_deszip": "#660099",
    "texto_btn_deszip": "#ff3cac",
    "borda_btn_deszip": "#00fff7"
}

# ==========================
# FUNÇÕES DE LÓGICA (ARQUIVOS)
# ==========================
def carregar_caminhos_salvos():
    """Carrega os caminhos dos arquivos ZIP salvos no JSON."""
    if os.path.exists(CAMINHO_JSON):
        try:
            with open(CAMINHO_JSON, "r") as f:
                dados = json.load(f)
                for slot_str, caminho in dados.items():
                    slot = int(slot_str)
                    if os.path.exists(caminho):
                        arquivos_zip[slot] = caminho
                        labels[slot].configure(text=os.path.basename(caminho))
                    else:
                        arquivos_zip[slot] = None
                        labels[slot].configure(text=f"Slot {slot}: Arquivo não encontrado")
        except Exception as e:
            print(f"Erro ao carregar JSON: {e}")
            for slot in arquivos_zip:
                arquivos_zip[slot] = None
                labels[slot].configure(text=f"Slot {slot}: Nenhum arquivo selecionado")
    else:
        for slot in arquivos_zip:
            arquivos_zip[slot] = None
            labels[slot].configure(text=f"Slot {slot}: Nenhum arquivo selecionado")

def salvar_caminhos():
    """Salva os caminhos dos arquivos ZIP no JSON."""
    with open(CAMINHO_JSON, "w") as f:
        dados_para_salvar = {str(k): v for k, v in arquivos_zip.items() if v is not None}
        json.dump(dados_para_salvar, f)

def escolher_arquivo(slot):
    caminho = filedialog.askopenfilename(
        filetypes=[("Arquivos ZIP e RAR", "*.zip *.rar"), ("Arquivos ZIP", "*.zip"), ("Arquivos RAR", "*.rar")]
    )
    if caminho:
        arquivos_zip[slot] = caminho
        nome_arquivo = os.path.basename(caminho)
        labels[slot].configure(text=nome_arquivo)
        botao_deszipar[slot].configure(text=f"Deszipar {nome_arquivo}")  # Atualiza texto do botão aqui
        salvar_caminhos()


def descompactar(slot):
    """Descompacta o arquivo ZIP selecionado no slot."""
    caminho = arquivos_zip.get(slot)
    if not caminho or not os.path.exists(caminho):
        print(f"Slot {slot}: Arquivo não encontrado ou não selecionado.")
        return

    try:
        pasta_destino = os.path.dirname(caminho)
        # Limpa arquivos/pastas que já existem na pasta do ZIP
        with zipfile.ZipFile(caminho, 'r') as zip_ref:
            for nome_arquivo in zip_ref.namelist():
                destino = os.path.join(pasta_destino, nome_arquivo)
                if os.path.isfile(destino):
                    os.remove(destino)
                elif os.path.isdir(destino):
                    shutil.rmtree(destino)
        # Extrai para a mesma pasta do ZIP
        Archive(caminho).extractall(pasta_destino)
    except Exception as e:
        print(f"Slot {slot}: Erro ao extrair {caminho}: {e}")

# ==========================
# FUNÇÕES DE CORES E CUSTOMIZAÇÃO
# ==========================
def salvar_cores():
    """Salva as cores personalizadas no JSON."""
    with open(CAMINHO_CORES, "w") as f:
        json.dump(cores, f)

def carregar_cores():
    """Carrega as cores personalizadas do JSON."""
    if os.path.exists(CAMINHO_CORES):
        try:
            with open(CAMINHO_CORES, "r") as f:
                data = json.load(f)
                for k in cores.keys():
                    if k in data:
                        cores[k] = data[k]
        except Exception as e:
            print(f"Erro ao carregar cores: {e}")

def atualizar_cores():
    """Atualiza as cores de todos os elementos da interface."""
    janela.configure(fg_color=cores["fundo_janela"])
    frame_slots.configure(fg_color=cores["fundo_frame"], border_color=cores["borda_frame"])
    frame_config.configure(fg_color=cores["fundo_frame"], border_color=cores["borda_frame"])
    for i in range(1, 4):
        labels[i].configure(text_color=cores["texto_label"])
        botao_selecionar[i].configure(
            fg_color=cores["fundo_btn_sel"],
            hover_color=cores["hover_btn_sel"],
            text_color=cores["texto_btn_sel"],
            border_color=cores["borda_btn_sel"])
        botao_deszipar[i].configure(
            fg_color=cores["fundo_btn_deszip"],
            hover_color=cores["hover_btn_deszip"],
            text_color=cores["texto_btn_deszip"],
            border_color=cores["borda_btn_deszip"])
    for child in frame_config.winfo_children():
        if isinstance(child, ctk.CTkLabel):
            child.configure(text_color=cores["texto_label"])
        if isinstance(child, ctk.CTkButton):
            child.configure(
                fg_color=cores["fundo_btn_sel"],
                hover_color=cores["hover_btn_sel"],
                text_color=cores["texto_btn_sel"],
                border_color=cores["borda_btn_sel"])

def criar_seletor_cor(nome_cor, texto, linha):
    """Cria um seletor de cor para personalizar as cores da interface."""
    def alterar_cor():
        cor_selecionada = colorchooser.askcolor(color=cores[nome_cor], title="Escolha a cor")[1]
        if cor_selecionada:
            cores[nome_cor] = cor_selecionada
            atualizar_cores()
            salvar_cores()

    label = ctk.CTkLabel(frame_config, text=texto, font=fonte_cyber, text_color=cores["texto_label"])
    label.grid(row=linha, column=0, padx=10, pady=5, sticky="w")

    btn = ctk.CTkButton(frame_config, text="Escolher Cor", font=fonte_cyber,
                        command=alterar_cor,
                        fg_color=cores["fundo_btn_sel"],
                        hover_color=cores["hover_btn_sel"],
                        text_color=cores["texto_btn_sel"],
                        border_color=cores["borda_btn_sel"])
    btn.grid(row=linha, column=1, padx=10, pady=5, sticky="ew")

# ==========================
# FUNÇÕES DE LAYOUT/INTERFACE
# ==========================
def criar_interface():
    ctk.set_appearance_mode("dark")
    global janela, frame_slots, frame_config, tabs
    janela = ctk.CTk()
    janela.title("InuZiper")
    janela.geometry("600x600")
    janela.resizable(False, False)

    # Adicionar suporte para ícone na barra de tarefas
    if os.name == 'nt':
        import ctypes
        app_id = 'seu_app.InuZiper'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    try:
        janela.iconbitmap(resource_path("icon.ico"))
        print("Ícone carregado com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar o ícone: {e}")

    carregar_cores()

    tabs = ctk.CTkTabview(janela)
    tabs.pack(padx=20, pady=20, fill="both", expand=True)
    tabs.add("Slots")
    tabs.add("Configurações")

    # Frame para os slots
    global frame_slots
    frame_slots = ctk.CTkFrame(tabs.tab("Slots"), corner_radius=10, border_width=3, border_color=cores["borda_frame"], fg_color=cores["fundo_frame"])
    frame_slots.pack(expand=True, fill="both", padx=20, pady=20)

    # Frame para as configurações
    global frame_config
    frame_config = ctk.CTkFrame(tabs.tab("Configurações"), corner_radius=10, border_width=3, border_color=cores["borda_frame"], fg_color=cores["fundo_frame"])
    frame_config.pack(expand=True, fill="both", padx=20, pady=20)

    # Criação dos elementos nos slots
    for i in range(1, 4):
        labels[i] = ctk.CTkLabel(frame_slots,
                                 text=f"Slot {i}: Nenhum arquivo selecionado",
                                 font=fonte_cyber,
                                 text_color=cores["texto_label"],
                                 anchor="w")
        labels[i].pack(pady=(15, 5), fill="x", padx=40)

        botao_selecionar[i] = ctk.CTkButton(frame_slots,
                                text=f"Selecionar ZIP para Slot {i}",
                                font=fonte_cyber,
                                fg_color=cores["fundo_btn_sel"],
                                hover_color=cores["hover_btn_sel"],
                                text_color=cores["texto_btn_sel"],
                                border_width=2,
                                border_color=cores["borda_btn_sel"],
                                corner_radius=8,
                                width=250,
                                command=lambda i=i: escolher_arquivo(i))
        botao_selecionar[i].pack(pady=5)

        botao_deszipar[i] = ctk.CTkButton(frame_slots,
                                   text=f"Deszipar Slot {i}",
                                   font=fonte_cyber,
                                   fg_color=cores["fundo_btn_deszip"],
                                   hover_color=cores["hover_btn_deszip"],
                                   text_color=cores["texto_btn_deszip"],
                                   border_width=2,
                                   border_color=cores["borda_btn_deszip"],
                                   corner_radius=8,
                                   width=250,
                                   command=lambda i=i: descompactar(i))
        botao_deszipar[i].pack(pady=(0, 15))

    # Criação dos seletores de cores
    nomes_cores = {
        "fundo_janela": "Fundo da Janela",
        "fundo_frame": "Fundo dos Frames",
        "borda_frame": "Borda dos Frames",
        "texto_label": "Texto dos Labels",
        "fundo_btn_sel": "Fundo dos Botões Selecionar",
        "hover_btn_sel": "Hover dos Botões Selecionar",
        "texto_btn_sel": "Texto dos Botões Selecionar",
        "borda_btn_sel": "Borda dos Botões Selecionar",
        "fundo_btn_deszip": "Fundo dos Botões Deszipar",
        "hover_btn_deszip": "Hover dos Botões Deszipar",
        "texto_btn_deszip": "Texto dos Botões Deszipar",
        "borda_btn_deszip": "Borda dos Botões Deszipar"
    }
    for idx, (chave, texto) in enumerate(nomes_cores.items()):
        criar_seletor_cor(chave, texto, idx)

# ==========================
# INICIALIZAÇÃO DA INTERFACE
# ==========================
if __name__ == "__main__":
    criar_interface()
    carregar_caminhos_salvos()
    atualizar_cores()
    janela.mainloop()
