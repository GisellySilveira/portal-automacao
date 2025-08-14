# app.py
import streamlit as st
import os
# Lembre-se de adicionar as importações necessárias para o processamento, como io e zipfile
import io
import zipfile

# Importa a função do nosso "depósito"
from processador_excel import processar_arquivo_excel 

st.set_page_config(layout="wide")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    # --- A MÁGICA ACONTECE AQUI ---
    # O Streamlit vai procurar por um arquivo chamado 'logo.png' na mesma pasta.
    st.image("logoship.png", width=200) # Você pode ajustar o 'width' para mudar o tamanho.
    
    st.title("Portal de Automação")
    
    escolha = st.radio(
        "Escolha a automação:",
        ("Processador de Excel", "Processador de PDF")
    )
    st.info("Este portal foi criado para automatizar tarefas repetitivas.")

# --- CONTEÚDO PRINCIPAL ---

if escolha == "Processador de Excel":
    st.header("1. Processador de Tabelas FedEx (Modelo Excel)")
    st.write("Faça o upload da planilha modelo da FedEx (.xlsx) para gerar os arquivos CSV finais.")

    arquivo_excel = st.file_uploader("Escolha a planilha Excel aqui", type=["xlsx"], key="excel_uploader")
    
    if arquivo_excel is not None:
        if st.button("Processar Planilha Excel"):
            with st.spinner("Aguarde... Processando a planilha e gerando arquivos..."):
                try:
                    # Chama a função de processamento
                    arquivos_gerados = processar_arquivo_excel(arquivo_excel)
                    
                    if arquivos_gerados:
                        # Cria um arquivo ZIP em memória
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
                            for arquivo in arquivos_gerados:
                                zip_file.writestr(arquivo['nome'], arquivo['dados'])
                        
                        st.success("Planilha processada com sucesso!")
                        
                        # Oferece o botão de download para o ZIP
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
                    st.error(e)

elif escolha == "Processador de PDF":
    st.header("2. Processador de Tabelas FedEx (Contrato PDF)")
    st.write("Funcionalidade em desenvolvimento...")
    # (O código para o PDF virá aqui depois)