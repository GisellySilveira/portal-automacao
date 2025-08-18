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

elif escolha_topico == "Tabelas de Frete":
    st.header("Ferramentas de Processamento de Tabelas de Frete")
    st.write("Selecione uma das opções abaixo para iniciar o processamento.")

    # --- MENU EXPANSÍVEL PARA A FEDEX ---
    with st.expander("✈️ FedEx", expanded=True): # expanded=True deixa aberto por padrão
        
        # Cria duas abas para organizar USA e Brasil
        tab_fedex_usa, tab_fedex_br = st.tabs(["FedEx USA", "FedEx Brasil"])

        with tab_fedex_usa:
            col_logo_usa, col_uploader_usa = st.columns([1, 2]) # Colunas para alinhar
            with col_logo_usa:
                st.image("logo_fedex.png", width=150)
            with col_uploader_usa:
                st.subheader("Processador de Modelo Excel (USA)")
                st.file_uploader("Escolha a planilha FedEx USA", key="fedex_usa_excel")

        with tab_fedex_br:
            col_logo_br, col_uploader_br = st.columns([1, 2])
            with col_logo_br:
                st.image("logo_fedex.png", width=150)
            with col_uploader_br:
                st.subheader("Processador de Contrato PDF (Brasil)")
                arquivo_fedex_br = st.file_uploader(
                    "Faça o upload do contrato FedEx Brasil", 
                    type=["pdf"], 
                    key="fedex_br_uploader"
                )
                if arquivo_fedex_br:
                    tipo_proc_br = st.radio(
                        "Tipo de Tabela:", ("Exportação", "Importação"), 
                        key="fedex_br_tipo", horizontal=True
                    )
                    st.button("Processar FedEx Brasil", key="btn_fedex_br")

    # --- MENU EXPANSÍVEL PARA A UPS ---
    with st.expander("📦 UPS"):
        col_logo_ups, col_uploaders_ups = st.columns([1, 2])
        with col_logo_ups:
            st.image("logo_ups.png", width=100)
        with col_uploaders_ups:
            st.subheader("UPS Brasil")
            st.file_uploader("Escolha o arquivo UPS Brasil", key="ups_br")
            st.subheader("UPS México")
            st.file_uploader("Escolha o arquivo UPS México", key="ups_mx")
            st.subheader("UPS USA")
            st.file_uploader("Escolha o arquivo UPS USA", key="ups_usa")

    # --- MENU EXPANSÍVEL PARA A DHL ---
    with st.expander("🚚 DHL"):
        col_logo_dhl, col_uploader_dhl = st.columns([1, 2])
        with col_logo_dhl:
            st.image("logo_dhl.png", width=150)
        with col_uploader_dhl:
            st.subheader("Processador de Contrato DHL")
            arquivo_dhl = st.file_uploader(
                "Faça o upload do contrato DHL", 
                type=["xlsx", "pdf"], 
                key="dhl_uploader"
            )
            if arquivo_dhl:
                tipo_proc_dhl = st.radio(
                    "Tipo de Tabela:", ("Exportação", "Importação"),
                    key="dhl_tipo", horizontal=True
                )
                st.button("Processar Tabela DHL", key="btn_dhl")
        
elif escolha_topico == "RECOM":
    st.header("Módulo RECOM")
    st.info("Funcionalidade em desenvolvimento...")

elif escolha_topico == "Troquecommerce":
    st.header("Módulo Troquecommerce")
    st.info("Funcionalidade em desenvolvimento...")
