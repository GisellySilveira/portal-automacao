# Nome do arquivo: app.py

import streamlit as st
import os

# Importa a função do nosso "depósito"
from processador_excel import processar_arquivo_excel 

st.set_page_config(layout="wide")
st.title("🤖 Portal de Automação da Empresa")
st.markdown("---")

# --- Seção 1: Automação de Tabelas FedEx (EXCEL) ---
st.header("1. Processador de Tabelas FedEx (Modelo Excel)")
st.write("Faça o upload da planilha modelo da FedEx (.xlsx) para gerar os arquivos CSV finais.")

arquivo_excel = st.file_uploader("Escolha a planilha Excel aqui", type=["xlsx"], key="excel_uploader")

if arquivo_excel is not None:
    if st.button("Processar Planilha Excel"):
        
        # Mostra uma mensagem de "carregando" para o usuário
        with st.spinner("Aguarde... Processando a planilha..."):
            
            # O Streamlit salva o arquivo em memória. Precisamos salvá-lo em disco
            # para que nosso script consiga lê-lo.
            PASTA_INPUT = os.path.join(os.getcwd(), "arquivos_recebidos")
            os.makedirs(PASTA_INPUT, exist_ok=True)
            caminho_temporario_excel = os.path.join(PASTA_INPUT, arquivo_excel.name)
            
            with open(caminho_temporario_excel, "wb") as f:
                f.write(arquivo_excel.getbuffer())
            
            # Define onde os resultados serão salvos
            PASTA_OUTPUT = os.path.join(os.getcwd(), "arquivos_processados")
            os.makedirs(PASTA_OUTPUT, exist_ok=True)
            
            # --- A MÁGICA ACONTECE AQUI ---
            # Chama a função do nosso outro arquivo, passando os caminhos
            try:
                pasta_final = processar_arquivo_excel(caminho_temporario_excel, PASTA_OUTPUT)
                
                st.success("Planilha processada com sucesso!")
                st.balloons() # Comemoração! :)
                st.write(f"✔ Arquivos salvos na pasta: `{pasta_final}`")
                st.info("Você pode encontrar os resultados na pasta 'arquivos_processados' dentro da pasta do projeto.")

            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a planilha:")
                st.error(e)

# --- Seção 2: Automação de Tabelas FedEx (PDF) ---
# (Por enquanto, deixamos esta seção desconectada)
st.markdown("---")
st.header("2. Processador de Tabelas FedEx (Contrato PDF)")
st.write("Faça o upload do contrato em PDF da FedEx para gerar os arquivos CSV finais.")
arquivo_pdf = st.file_uploader("Escolha o arquivo PDF aqui", type=["pdf"], key="pdf_uploader")
if arquivo_pdf is not None:
    if st.button("Processar Arquivo PDF"):
        st.info("Funcionalidade em desenvolvimento...")