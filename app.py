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
    with st.expander("✈️ FedEx"):
        # Coloca a logo e o uploader em colunas para um visual mais limpo
        col_logo, col_uploader = st.columns([1, 4]) # A coluna do uploader é 4x maior
        
        with col_logo:
            st.image("logo_fedex.png", width=100) # Ajuste o tamanho se necessário

        with col_uploader:
            arquivo_fedex = st.file_uploader(
                "Faça o upload do contrato FedEx (Excel ou PDF)", 
                type=["xlsx", "pdf"], 
                key="fedex_uploader"
            )

        # Só mostra as opções DEPOIS que um arquivo for enviado
        if arquivo_fedex is not None:
            st.success(f"Arquivo '{arquivo_fedex.name}' carregado.")
            
            tipo_processamento = st.radio(
                "Qual o tipo de tabela neste arquivo?",
                ("Exportação", "Importação"),
                key="fedex_tipo",
                horizontal=True # Deixa os botões lado a lado
            )
            
            if st.button("Processar Tabela FedEx", key="btn_fedex"):
                st.info(f"Processando arquivo FedEx como '{tipo_processamento}'...")
                # Aqui entrará a chamada para a função de back-end

    # --- MENU EXPANSÍVEL PARA A UPS ---
    with st.expander("📦 UPS"):
        col_logo_ups, col_uploader_ups = st.columns([1, 4])
        with col_logo_ups:
            st.image("logo_ups.png", width=100)
        
        with col_uploader_ups:
            # Para a UPS, mantemos separado por país, pois são tabelas diferentes
            st.subheader("UPS Brasil")
            st.file_uploader("Escolha o arquivo UPS Brasil", key="ups_br")
            
            st.subheader("UPS México")
            st.file_uploader("Escolha o arquivo UPS México", key="ups_mx")

            st.subheader("UPS USA")
            st.file_uploader("Escolha o arquivo UPS USA", key="ups_usa")


    # --- MENU EXPANSÍVEL PARA A DHL ---
    with st.expander("🚚 DHL"):
        col_logo_dhl, col_uploader_dhl = st.columns([1, 4])
        with col_logo_dhl:
            st.image("logo_dhl.png", width=150) # Logo da DHL é mais larga
        
        with col_uploader_dhl:
            arquivo_dhl = st.file_uploader(
                "Faça o upload do contrato DHL", 
                type=["xlsx", "pdf"], 
                key="dhl_uploader"
            )

        if arquivo_dhl is not None:
            st.success(f"Arquivo '{arquivo_dhl.name}' carregado.")

            tipo_processamento_dhl = st.radio(
                "Qual o tipo de tabela neste arquivo?",
                ("Exportação", "Importação"),
                key="dhl_tipo",
                horizontal=True
            )
            
            if st.button("Processar Tabela DHL", key="btn_dhl"):
                st.info(f"Processando arquivo DHL como '{tipo_processamento_dhl}'...")
                # Aqui entrará a chamada para a função de back-end
        
elif escolha_topico == "RECOM":
    st.header("Módulo RECOM")
    st.info("Funcionalidade em desenvolvimento...")

elif escolha_topico == "Troquecommerce":
    st.header("Módulo Troquecommerce")
    st.info("Funcionalidade em desenvolvimento...")