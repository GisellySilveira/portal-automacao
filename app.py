import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Portal de Automação ShipSmart")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("logoship.png", width=200)
    st.title("Portal ShipSmart")
    
    # Menu principal de navegação
    escolha_topico = st.selectbox(
        "Selecione o Módulo:",
        ("Página Inicial", "Tabelas de Frete", "RECOM", "Troquecommerce")
    )

st.markdown("---")


# --- CONTEÚDO PRINCIPAL ---

if escolha_topico == "Página Inicial":
    st.header("Bem-vindo(a) ao Portal de Automação! 👋")
    st.info("Utilize o menu à esquerda para navegar entre as ferramentas disponíveis.")
    st.markdown("""
        Este portal foi criado para centralizar e simplificar tarefas repetitivas.
        - **Tabelas de Frete:** Faça o upload de contratos de transportadoras e receba as tabelas prontas para o sistema.
        - **RECOM:** (Descrição da automação RECOM aqui).
        - **Troquecommerce:** (Descrição da automação Troquecommerce aqui).
    """)

elif escolha_topico == "Tabelas de Frete":
    st.header("Ferramentas de Processamento de Tabelas de Frete")
    st.write("Selecione uma das opções abaixo para iniciar o processamento.")

    # --- MENU EXPANSÍVEL PARA A FEDEX ---
    with st.expander("✈️ FedEx"):
        st.subheader("FedEx USA (Modelo Excel)")
        arquivo_excel_usa = st.file_uploader("Escolha a planilha FedEx USA (.xlsx)", type=["xlsx"], key="fedex_usa_excel")
        if arquivo_excel_usa:
            st.button("Processar FedEx USA", key="btn_fedex_usa")

        st.divider() # Linha divisória
        
        st.subheader("FedEx Brasil (Contrato PDF)")
        col1, col2 = st.columns(2)
        with col1:
            pdf_br_export = st.file_uploader("Upload do PDF de Exportação", type=["pdf"], key="fedex_br_export")
            if pdf_br_export:
                st.button("Processar Exportação", key="btn_fedex_br_export")
        with col2:
            pdf_br_import = st.file_uploader("Upload do PDF de Importação", type=["pdf"], key="fedex_br_import")
            if pdf_br_import:
                st.button("Processar Importação", key="btn_fedex_br_import")

    # --- MENU EXPANSÍVEL PARA A UPS ---
    with st.expander("📦 UPS"):
        st.subheader("UPS Brasil")
        st.file_uploader("Escolha o arquivo UPS Brasil", key="ups_br")

        st.divider()
        
        st.subheader("UPS México")
        st.file_uploader("Escolha o arquivo UPS México", key="ups_mx")
        
        st.divider()

        st.subheader("UPS USA")
        st.file_uploader("Escolha o arquivo UPS USA", key="ups_usa")

    # --- MENU EXPANSÍVEL PARA A DHL ---
    with st.expander("🚚 DHL"):
        st.subheader("DHL")
        col1, col2 = st.columns(2)
        with col1:
            dhl_export = st.file_uploader("Upload de Exportação", type=["pdf", "xlsx"], key="dhl_export")
        with col2:
            dhl_import = st.file_uploader("Upload de Importação", type=["pdf", "xlsx"], key="dhl_import")
        
elif escolha_topico == "RECOM":
    st.header("Módulo RECOM")
    st.info("Funcionalidade em desenvolvimento...")

elif escolha_topico == "Troquecommerce":
    st.header("Módulo Troquecommerce")
    st.info("Funcionalidade em desenvolvimento...")