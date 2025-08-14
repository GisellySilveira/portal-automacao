# Nome do arquivo: app.py

import streamlit as st
import os
import io
import zipfile

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
        
        with st.spinner("Aguarde... Processando a planilha e gerando arquivos..."):
            try:
                # --- A MÁGICA ACONTECE AQUI ---
                # 1. Chama a função de processamento, que agora retorna uma lista de arquivos
                arquivos_gerados = processar_arquivo_excel(arquivo_excel)
                
                if arquivos_gerados:
                    # 2. Cria um arquivo ZIP em memória
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for arquivo in arquivos_gerados:
                            # Adiciona cada arquivo (com seu nome e dados) ao ZIP
                            zip_file.writestr(arquivo['nome'], arquivo['dados'])
                    
                    st.success("Planilha processada com sucesso!")
                    
                    # 3. Oferece o botão de download para o ZIP
                    st.download_button(
                        label="✔️ Baixar Todos os Arquivos (.zip)",
                        data=zip_buffer.getvalue(),
                        file_name="resultados_processados.zip",
                        mime="application/zip"
                    )
                else:
                    st.warning("Nenhum arquivo foi gerado. A planilha pode estar vazia ou em um formato inesperado.")

            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a planilha:")
                st.error(e) # Mostra o erro real na tela para depuração

# --- Seção 2: Automação de Tabelas FedEx (PDF) ---
# (Deixamos desconectada por enquanto)
st.markdown("---")
st.header("2. Processador de Tabelas FedEx (Contrato PDF)")
st.write("Faça o upload do contrato em PDF da FedEx para gerar os arquivos CSV finais.")
arquivo_pdf = st.file_uploader("Escolha o arquivo PDF aqui", type=["pdf"], key="pdf_uploader")
if arquivo_pdf is not None:
    if st.button("Processar Arquivo PDF"):
        st.info("Funcionalidade em desenvolvimento...")