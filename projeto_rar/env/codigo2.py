import customtkinter as ctk
from tkinter import filedialog
from pyunpack import Archive
import os
import zipfile
import json
import shutil

PASTA_DESTINO = "C:/MeusArquivosDescompactados"
CAMINHO_JSON = "caminhos_zips.json"

arquivos_zip = {1: None, 2: None, 3: None}
labels = {}

# Fonte legal e moderna, mas legível
fonte_cyber = ("Consolas", 14, "bold")

def carregar_caminhos_salvos():
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
    with open(CAMINHO_JSON, "w") as f:
        dados_para_salvar = {str(k): v for k, v in arquivos_zip.items() if v is not None}
        json.dump(dados_para_salvar, f)

def escolher_arquivo(slot):
    caminho = filedialog.askopenfilename(filetypes=[("Arquivos ZIP", "*.zip")])
    if caminho:
        arquivos_zip[slot] = caminho
        labels[slot].configure(text=os.path.basename(caminho))
        salvar_caminhos()

def descompactar(slot):
    caminho = arquivos_zip.get(slot)
    if not caminho or not os.path.exists(caminho):
        print(f"Slot {slot}: Arquivo não encontrado ou não selecionado.")
        return

    try:
        with zipfile.ZipFile(caminho, 'r') as zip_ref:
            for nome_arquivo in zip_ref.namelist():
                destino = os.path.join(PASTA_DESTINO, nome_arquivo)
                if os.path.isfile(destino):
                    os.remove(destino)
                elif os.path.isdir(destino):
                    shutil.rmtree(destino)

        Archive(caminho).extractall(PASTA_DESTINO)
        print(f"Slot {slot}: Extraído com sucesso - {caminho}")

    except Exception as e:
        print(f"Slot {slot}: Erro ao extrair {caminho}: {e}")

# Configurações cyberpunk
ctk.set_appearance_mode("dark")

janela = ctk.CTk()
janela.title("Descompactador Cyberpunk")
janela.geometry("600x450")
janela.resizable(False, False)
janela.configure(fg_color="#1b003b")  # fundo roxo escuro

# Frame com borda neon azul
frame_slots = ctk.CTkFrame(janela, corner_radius=10, fg_color="#0a0a23", border_width=3, border_color="#00fff7")
frame_slots.pack(padx=20, pady=20, fill="both", expand=True)

for i in range(1, 4):
    labels[i] = ctk.CTkLabel(frame_slots,
                             text=f"Slot {i}: Nenhum arquivo selecionado",
                             font=fonte_cyber,
                             text_color="#ff3cac",  # neon pink
                             anchor="w")
    labels[i].pack(pady=(10, 5), fill="x")

    btn_sel = ctk.CTkButton(frame_slots,
                            text=f"Selecionar ZIP para Slot {i}",
                            font=fonte_cyber,
                            fg_color="#1b003b",
                            hover_color="#330066",
                            text_color="#00fff7",  # neon blue
                            border_width=2,
                            border_color="#ff3cac",  # neon pink
                            corner_radius=8,
                            command=lambda i=i: escolher_arquivo(i))
    btn_sel.pack(pady=5, fill="x")

    btn_deszip = ctk.CTkButton(frame_slots,
                               text=f"Deszipar Slot {i}",
                               font=fonte_cyber,
                               fg_color="#330066",
                               hover_color="#660099",
                               text_color="#ff3cac",
                               border_width=2,
                               border_color="#00fff7",
                               corner_radius=8,
                               command=lambda i=i: descompactar(i))
    btn_deszip.pack(pady=(0, 15), fill="x")

carregar_caminhos_salvos()

janela.mainloop()
