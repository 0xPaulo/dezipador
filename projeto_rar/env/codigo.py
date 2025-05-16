import tkinter as tk
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

# Carregar caminhos salvos do JSON
def carregar_caminhos_salvos():
    if os.path.exists(CAMINHO_JSON):
        try:
            with open(CAMINHO_JSON, "r") as f:
                dados = json.load(f)
                for slot_str, caminho in dados.items():
                    slot = int(slot_str)
                    if os.path.exists(caminho):
                        arquivos_zip[slot] = caminho
                        labels[slot].config(text=os.path.basename(caminho))
                    else:
                        arquivos_zip[slot] = None
                        labels[slot].config(text=f"Slot {slot}: Arquivo não encontrado")
        except Exception as e:
            print(f"Erro ao carregar JSON: {e}")
            # Em caso de erro, iniciar com valores padrão
            for slot in arquivos_zip:
                arquivos_zip[slot] = None
                labels[slot].config(text=f"Slot {slot}: Nenhum arquivo selecionado")
    else:
        # Se não existir o JSON, iniciar normalmente
        for slot in arquivos_zip:
            arquivos_zip[slot] = None
            labels[slot].config(text=f"Slot {slot}: Nenhum arquivo selecionado")

# Salvar os caminhos no JSON
def salvar_caminhos():
    with open(CAMINHO_JSON, "w") as f:
        # Convertemos as chaves para string, pois JSON não aceita int como chave
        dados_para_salvar = {str(k): v for k, v in arquivos_zip.items() if v is not None}
        json.dump(dados_para_salvar, f)

def escolher_arquivo(slot):
    caminho = filedialog.askopenfilename(filetypes=[("Arquivos ZIP", "*.zip")])
    if caminho:
        arquivos_zip[slot] = caminho
        labels[slot].config(text=os.path.basename(caminho))
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

# Interface
janela = tk.Tk()
janela.title("Descompactador com Slots Salvos")

for i in range(1, 4):
    labels[i] = tk.Label(janela, text=f"Slot {i}: Nenhum arquivo selecionado", width=50, anchor="w")
    labels[i].pack(pady=2)

    tk.Button(janela, text=f"Selecionar ZIP para Slot {i}", command=lambda i=i: escolher_arquivo(i)).pack(pady=2)
    tk.Button(janela, text=f"Deszipar Slot {i}", command=lambda i=i: descompactar(i)).pack(pady=5)

# Carrega ao abrir
carregar_caminhos_salvos()

janela.mainloop()
