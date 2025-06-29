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
import win32api  # Adicionado para obter versão de executáveis

def resource_path(rel_path):
    """Funciona para o .py e também para o .exe"""
    try:
        base_path = sys._MEIPASS  # Quando executado pelo PyInstaller
    except Exception:
        base_path = os.path.abspath(".")  # Quando executado diretamente pelo Python
    return os.path.join(base_path, rel_path)

# NOVO: Caminho para temas
CAMINHO_TEMAS = resource_path("temas/temas.json")
CAMINHO_TEMA_ATUAL = Path.home() / "Documents" / "InuSoftware" / "InuZiper" / "InuConfig" / "tema_atual.json"

def carregar_temas():
    """Carrega todos os temas disponíveis do arquivo temas.json."""
    with open(CAMINHO_TEMAS, "r", encoding="utf-8") as f:
        return json.load(f)["temas"]

def salvar_tema_atual(nome_tema):
    with open(CAMINHO_TEMA_ATUAL, "w", encoding="utf-8") as f:
        json.dump({"tema": nome_tema}, f)

def carregar_tema_atual():
    if os.path.exists(CAMINHO_TEMA_ATUAL):
        try:
            with open(CAMINHO_TEMA_ATUAL, "r", encoding="utf-8") as f:
                return json.load(f).get("tema")
        except:
            return None
    return None

def aplicar_tema(nome_tema):
    """Aplica o tema selecionado ao app."""
    temas = carregar_temas()
    if nome_tema in temas:
        tema = temas[nome_tema]["cores"]
        cores.update(tema)
        atualizar_cores()
        salvar_cores()
        salvar_tema_atual(nome_tema)
        # Atualiza a seleção visual dos temas
        atualizar_selecao_tema(nome_tema)

# ==========================
# CONFIGURAÇÕES E CONSTANTES
# ==========================

# Caminho para a pasta "inuconfig" dentro de "Documentos"
PASTA_CONFIG = Path.home() / "Documents" / "InuSoftware" / "InuZiper" / "InuConfig"
PASTA_CONFIG.mkdir(parents=True, exist_ok=True)  # Cria a pasta se não existir

# Atualiza os caminhos dos arquivos JSON
CAMINHO_JSON = PASTA_CONFIG / "caminhos_zips.json"
CAMINHO_CORES = PASTA_CONFIG / "cores_tema.json"
CAMINHO_VERSAO = PASTA_CONFIG / "ultima_versao.json"  # Novo arquivo para salvar a última versão

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


def obter_versao_arquivo(caminho_arquivo):
    """Obtém a versão de um arquivo executável (Windows)"""
    try:
        info = win32api.GetFileVersionInfo(caminho_arquivo, '\\')
        version = "%d.%d.%d.%d" % (
            info['FileVersionMS'] // 65536,
            info['FileVersionMS'] % 65536,
            info['FileVersionLS'] // 65536,
            info['FileVersionLS'] % 65536
        )
        return version
    except:
        return None

def salvar_ultima_versao(arquivo, versao):
    """Salva a última versão descompactada no arquivo JSON"""
    with open(CAMINHO_VERSAO, "w") as f:
        json.dump({"arquivo": arquivo, "versao": versao}, f)

def carregar_ultima_versao():
    """Carrega a última versão descompactada do arquivo JSON"""
    if os.path.exists(CAMINHO_VERSAO):
        try:
            with open(CAMINHO_VERSAO, "r") as f:
                return json.load(f)
        except:
            return {"arquivo": "Nenhum", "versao": "N/A"}
    return {"arquivo": "Nenhum", "versao": "N/A"}

def descompactar(slot):
    """Descompacta o arquivo ZIP selecionado no slot e mostra a versão do R1_ERP.exe extraído."""
    caminho = arquivos_zip.get(slot)
    if not caminho or not os.path.exists(caminho):
        print(f"Slot {slot}: Arquivo não encontrado ou não selecionado.")
        return

    try:
        pasta_destino = os.path.dirname(caminho)
        nome_exe = "R1_ERP.exe"
        caminho_exe = os.path.join(pasta_destino, nome_exe)

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

        # Agora pegar a versão do R1_ERP.exe extraído
        if os.path.exists(caminho_exe):
            versao = obter_versao_arquivo(caminho_exe)
            if versao:
                label_versao.configure(text=f"Versão descompactada: {nome_exe} - v{versao}")
                salvar_ultima_versao(nome_exe, versao)
            else:
                label_versao.configure(text="Não foi possível identificar a versão do R1_ERP.exe extraído")
        else:
            label_versao.configure(text="R1_ERP.exe não encontrado após extração")

    except Exception as e:
        print(f"Slot {slot}: Erro ao extrair {caminho}: {e}")
        label_versao.configure(text=f"Erro: {str(e)}")

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
    if 'label_versao' in globals():
        label_versao.configure(text_color=cores["texto_label"])

    # Atualizar frame de temas se existir
    if 'frame_temas' in globals():
        frame_temas.configure(fg_color=cores["fundo_frame"], border_color=cores["borda_frame"])
    if 'label_temas' in globals():
        label_temas.configure(text_color=cores["texto_label"])

# NOVA FUNÇÃO: Atualizar seleção visual do tema
def atualizar_selecao_tema(tema_selecionado):
    """Atualiza a seleção visual dos botões de tema."""
    if 'botoes_tema' in globals():
        for nome_tema, botao in botoes_tema.items():
            if nome_tema == tema_selecionado:
                # Tema selecionado - borda mais grossa e colorida
                botao.configure(border_width=4, border_color=cores["borda_frame"])
            else:
                # Tema não selecionado - borda fina
                botao.configure(border_width=2, border_color="#666666")

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
    global janela, frame_slots, frame_config, tabs, label_versao, frame_temas, label_temas, botoes_tema
    janela = ctk.CTk()
    janela.title("InuZiper")
    janela.geometry("600x650")
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

    # NOVO: Carregar temas e tema atual
    temas_disponiveis = carregar_temas()
    tema_salvo = carregar_tema_atual()

    tabs = ctk.CTkTabview(janela)
    tabs.pack(padx=20, pady=20, fill="both", expand=True)
    tabs.add("Slots")
    tabs.add("Configurações")

    # Frame para os slots
    global frame_slots
    frame_slots = ctk.CTkFrame(tabs.tab("Slots"), corner_radius=10, border_width=3, border_color=cores["borda_frame"], fg_color=cores["fundo_frame"])
    frame_slots.pack(expand=True, fill="both", padx=20, pady=20)

    # Frame para as configurações (agora rolável)
    global frame_config
    frame_config = ctk.CTkScrollableFrame(
        tabs.tab("Configurações"),
        corner_radius=10,
        border_width=3,
        border_color=cores["borda_frame"],
        fg_color=cores["fundo_frame"],
        width=560,  # ajuste conforme necessário
        height=500  # ajuste conforme necessário
    )
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

    # Adicionando label para mostrar a última versão descompactada
    ultima_versao = carregar_ultima_versao()
    label_versao = ctk.CTkLabel(frame_slots,
                                text=f"Última versão descompactada: {ultima_versao['arquivo']} - v{ultima_versao['versao']}",
                                font=fonte_cyber,
                                text_color=cores["texto_label"])
    label_versao.pack(pady=(10, 20))

    # NOVO: Seletor visual de temas com quadradinhos coloridos
    label_temas = ctk.CTkLabel(
        frame_config,
        text="🎨 Selecionar Tema:",
        font=fonte_cyber,
        text_color=cores["texto_label"]
    )
    label_temas.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")

    # Frame para os botões de tema
    frame_temas = ctk.CTkFrame(
        frame_config, 
        fg_color=cores["fundo_frame"],
        border_color=cores["borda_frame"],
        border_width=2,
        corner_radius=10
    )
    frame_temas.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

    # Criar botões para cada tema (agora como quadradinhos pequenos)
    botoes_tema = {}
    row = 0
    col = 0
    max_cols = 6  # Mais colunas para caber mais quadradinhos na linha

    for nome_tema, dados_tema in temas_disponiveis.items():
        cores_tema = dados_tema["cores"]

        def criar_comando_tema(tema):
            return lambda: aplicar_tema(tema)

        botao_tema = ctk.CTkButton(
            frame_temas,
            text="",  # Sem texto!
            width= 32,
            height=32,
            fg_color=cores_tema["fundo_btn_sel"],
            hover_color=cores_tema["hover_btn_sel"],
            border_width=2,
            border_color="#666666",
            corner_radius=6,
            command=criar_comando_tema(nome_tema)
        )

        botao_tema.grid(row=row, column=col, padx=8, pady=8)
        botoes_tema[nome_tema] = botao_tema

        col += 1
        if col >= max_cols:
            col = 0
            row += 1

    # Configurar grid do frame de temas para centralizar
    for i in range(max_cols):
        frame_temas.grid_columnconfigure(i, weight=1)

    # Configure o grid principal
    frame_config.grid_columnconfigure(0, weight=1)
    frame_config.grid_columnconfigure(1, weight=1)

    # Marcar tema atual como selecionado
    if tema_salvo:
        atualizar_selecao_tema(tema_salvo)

    # Criação dos seletores de cores (começando da linha 2 agora)
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
        criar_seletor_cor(chave, texto, idx+2)  # +2 para começar na linha 2

# ==========================
# INICIALIZAÇÃO DA INTERFACE
# ==========================
if __name__ == "__main__":
    criar_interface()
    carregar_caminhos_salvos()
    atualizar_cores()
    janela.mainloop()