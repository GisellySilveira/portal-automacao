import streamlit as st
import os
import io
import zipfile

# Tenta importar as funções de processamento. Se não encontrar, define funções de exemplo.
try:
    from processador_excel import processar_arquivo_excel
except ImportError:
    def processar_arquivo_excel(file):
        st.warning("Função 'processar_arquivo_excel' não encontrada. Usando dados de exemplo.")
        # Retorna uma lista de arquivos de exemplo para o download funcionar
        return [{'nome': 'exemplo_doc.csv', 'dados': 'exemplo;doc'}, {'nome': 'exemplo_notdoc.csv', 'dados': 'exemplo;notdoc'}]

# (Aqui entra a importação do processador de PDF quando estiver pronto)
# try:
#     from processador_pdf_br import processar_pdf_fedex_br
# except ImportError:
#     def processar_pdf_fedex_br(file, tipo):
#         st.warning("Função 'processar_pdf_fedex_br' não encontrada.")
#         return []


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Portal de Automação ShipSmart")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("logoship.png", width=200)
    st.title("Portal ShipSmart")
    
    escolha_topico = st.selectbox(
        "Selecione o Módulo:",
        ("Página Inicial", "Tabelas de Frete", "Tabela de Importação", "RECOM", "Troquecommerce")
    )

st.markdown("---")


# --- CONTEÚDO PRINCIPAL ---

if escolha_topico == "Página Inicial":
    st.header("Bem-vindo(a) ao Portal de Automação! 👋")
    st.info("Utilize o menu à esquerda para navegar entre as ferramentas disponíveis.")

elif escolha_topico == "Tabelas de Frete":
    st.header("Ferramentas de Processamento de Tabelas de Frete")
    st.write("Selecione uma das opções abaixo para iniciar o processamento.")

    # Botão para baixar modelo Excel
    st.markdown("---")
    col_info, col_download = st.columns([2, 1])
    with col_info:
        st.info("📥 **Precisa de um modelo?** Baixe o arquivo Excel modelo para preencher corretamente.")
    with col_download:
        try:
            with open("MODELO_TABELA_FRETE.xlsx", "rb") as f:
                st.download_button(
                    label="📥 Baixar Modelo Excel",
                    data=f,
                    file_name="MODELO_TABELA_FRETE.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.warning("Modelo não encontrado")
    st.markdown("---")

    # --- MENU EXPANSÍVEL PARA A FEDEX ---
    with st.expander("✈️ FedEx", expanded=True):
        col_logo_fedex, col_uploader_fedex = st.columns([1, 2])
        with col_logo_fedex:
            st.image("logo_fedex.png", width=150)
        with col_uploader_fedex:
            st.subheader("Processador de Modelo Excel")
            
            # Campo obrigatório para nome do cliente
            nome_cliente_fedex = st.text_input("Nome do Cliente*:", key="nome_cliente_fedex", 
                                               placeholder="Ex: ClienteXYZ")
            
            # Configurações em 4 colunas
            col_conv_moeda, col_margem, col_incremento, col_conv_peso = st.columns(4)
            
            with col_conv_moeda:
                usar_conversao_fedex = st.checkbox("💱 Conversão de moeda", value=False, key="usar_conv_fedex")
                taxa_conversao_fedex = st.number_input("Taxa:", 
                                                      min_value=0.01, 
                                                      value=1.0, 
                                                      step=0.01,
                                                      format="%.2f",
                                                      key="taxa_fedex",
                                                      help="Ex: 1.17 para EUR → USD",
                                                      disabled=not usar_conversao_fedex)
            
            with col_margem:
                adicionar_margem_fedex = st.checkbox("📊 Gerar margem", 
                                                     value=True, key="margem_fedex")
            
            with col_incremento:
                incremento_fedex = st.selectbox(
                    "⚖️ Incremento:",
                    options=[0.1, 0.5, 1.0],
                    format_func=lambda x: f"{x} kg ({int(x*1000)}g)",
                    key="incremento_fedex",
                    help="De quanto em quanto o peso aumenta"
                )
            
            with col_conv_peso:
                converter_peso_fedex = st.checkbox("🔄 lb → kg", value=False, key="conv_peso_fedex",
                                                   help="Converte pesos de libras para quilogramas")
            
            # Opções avançadas
            with st.expander("⚙️ Configurações Avançadas"):
                st.markdown("### 📊 Selecionar Serviços para Processar")
                st.info("Escolha quais serviços da FedEx você deseja processar:")
                col_priority, col_economy, col_cp = st.columns(3)
                with col_priority:
                    processar_priority = st.checkbox("✈️ Priority", value=True, key="proc_priority_fedex")
                with col_economy:
                    processar_economy = st.checkbox("📦 Economy", value=True, key="proc_economy_fedex")
                with col_cp:
                    processar_cp = st.checkbox("📮 CP", value=True, key="proc_cp_fedex")
            
            arquivo_excel_fedex = st.file_uploader("Escolha a planilha FedEx", type=["xlsx", "xls"], key="fedex_excel")
                
                # --- BOTÃO E LÓGICA DE PROCESSAMENTO AQUI ---
            if arquivo_excel_fedex:
                if st.button("Processar FedEx", key="btn_fedex"):
                    if not nome_cliente_fedex or nome_cliente_fedex.strip() == "":
                        st.error("❌ Por favor, preencha o nome do cliente.")
                    else:
                        with st.spinner("Aguarde... Processando a planilha FedEx..."):
                            try:
                                # Prepara lista de serviços a processar
                                servicos_processar = []
                                if processar_priority:
                                    servicos_processar.append('Priority')
                                if processar_economy:
                                    servicos_processar.append('Economy')
                                if processar_cp:
                                    servicos_processar.append('CP')
                                
                                if not servicos_processar:
                                    st.error("❌ Selecione pelo menos um serviço para processar!")
                                else:
                                    arquivos_gerados = processar_arquivo_excel(
                                        arquivo_excel_fedex, 
                                        transportadora='FEDEX',
                                        nome_cliente=nome_cliente_fedex.strip(),
                                        adicionar_margem=adicionar_margem_fedex,
                                        taxa_conversao=taxa_conversao_fedex if usar_conversao_fedex else 1.0,
                                        incremento_peso=incremento_fedex,
                                        converter_lb_para_kg=converter_peso_fedex,
                                        servicos_filtrar=servicos_processar,
                                        gerar_importacao=False,
                                        pais_importacao=None,
                                        iso_importacao=None
                                    )
                                if arquivos_gerados:
                                    zip_buffer = io.BytesIO()
                                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
                                        for arquivo in arquivos_gerados:
                                            zf.writestr(arquivo['nome'], arquivo['dados'])
                                    
                                        st.success(f"✅ Planilha processada com sucesso! {len(arquivos_gerados)} arquivos gerados.")
                                    st.download_button(
                                            label="📥 Baixar Todos os Arquivos (.zip)", 
                                            data=zip_buffer.getvalue(),
                                            file_name="resultados_FedEx.zip", 
                                            mime="application/zip",
                                            use_container_width=True
                                    )
                                else:
                                    st.warning("Nenhum arquivo foi gerado.")
                            except Exception as e:
                                st.error(f"❌ Ocorreu um erro: {e}")
                                import traceback
                                with st.expander("Detalhes do erro"):
                                    st.code(traceback.format_exc())

    # --- MENU EXPANSÍVEL PARA A UPS ---
    with st.expander("📦 UPS"):
        col_logo_ups, col_uploader_ups = st.columns([1, 2])
        with col_logo_ups:
            st.image("logo_ups.png", width=150)
        with col_uploader_ups:
            st.subheader("Processador de Modelo Excel")
            
            # Campo obrigatório para nome do cliente
            nome_cliente_ups = st.text_input("Nome do Cliente*:", key="nome_cliente_ups", 
                                            placeholder="Ex: ClienteXYZ")
            
            # Configurações em 4 colunas
            col_conv_moeda, col_margem, col_incremento, col_conv_peso = st.columns(4)
            
            with col_conv_moeda:
                usar_conversao_ups = st.checkbox("💱 Conversão de moeda", value=False, key="usar_conv_ups")
                taxa_conversao_ups = st.number_input("Taxa:", 
                                                    min_value=0.01, 
                                                    value=1.0, 
                                                    step=0.01,
                                                    format="%.2f",
                                                    key="taxa_ups",
                                                    help="Ex: 1.17 para EUR → USD",
                                                    disabled=not usar_conversao_ups)
            
            with col_margem:
                adicionar_margem_ups = st.checkbox("📊 Gerar margem", 
                                                  value=True, key="margem_ups")
            
            with col_incremento:
                incremento_ups = st.selectbox(
                    "⚖️ Incremento:",
                    options=[0.1, 0.5, 1.0],
                    format_func=lambda x: f"{x} kg ({int(x*1000)}g)",
                    key="incremento_ups",
                    help="De quanto em quanto o peso aumenta"
                )
            
            with col_conv_peso:
                converter_peso_ups = st.checkbox("🔄 lb → kg", value=False, key="conv_peso_ups",
                                                 help="Converte pesos de libras para quilogramas")
            
            
            arquivo_excel_ups = st.file_uploader("Escolha a planilha UPS", type=["xlsx", "xls"], key="ups_excel")
            
            if arquivo_excel_ups:
                if st.button("Processar UPS", key="btn_ups"):
                    if not nome_cliente_ups or nome_cliente_ups.strip() == "":
                        st.error("❌ Por favor, preencha o nome do cliente.")
                    else:
                        with st.spinner("Aguarde... Processando a planilha UPS..."):
                            try:
                                arquivos_gerados = processar_arquivo_excel(
                                    arquivo_excel_ups, 
                                    transportadora='UPS',
                                    nome_cliente=nome_cliente_ups.strip(),
                                    adicionar_margem=adicionar_margem_ups,
                                    taxa_conversao=taxa_conversao_ups if usar_conversao_ups else 1.0,
                                    incremento_peso=incremento_ups,
                                    converter_lb_para_kg=converter_peso_ups,
                                    gerar_importacao=False,
                                    pais_importacao=None,
                                    iso_importacao=None
                                )
                                if arquivos_gerados:
                                    zip_buffer = io.BytesIO()
                                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
                                        for arquivo in arquivos_gerados:
                                            zf.writestr(arquivo['nome'], arquivo['dados'])
                                    
                                    st.success(f"✅ Planilha processada com sucesso! {len(arquivos_gerados)} arquivos gerados.")
                                    st.download_button(
                                        label="📥 Baixar Todos os Arquivos (.zip)", 
                                        data=zip_buffer.getvalue(),
                                        file_name="resultados_UPS.zip", 
                                        mime="application/zip",
                                        use_container_width=True
                                    )
                                else:
                                    st.warning("Nenhum arquivo foi gerado.")
                            except Exception as e:
                                st.error(f"❌ Ocorreu um erro: {e}")
                                import traceback
                                with st.expander("Detalhes do erro"):
                                    st.code(traceback.format_exc())

    # --- MENU EXPANSÍVEL PARA A DHL ---
    with st.expander("🚚 DHL"):
        col_logo_dhl, col_uploader_dhl = st.columns([1, 2])
        with col_logo_dhl:
            st.image("logo_dhl.png", width=150)
        with col_uploader_dhl:
            st.subheader("Processador de Modelo Excel")
            
            # Campo obrigatório para nome do cliente
            nome_cliente_dhl = st.text_input("Nome do Cliente*:", key="nome_cliente_dhl", 
                                            placeholder="Ex: ClienteXYZ")
            
            # Configurações em 4 colunas
            col_conv_moeda, col_margem, col_incremento, col_conv_peso = st.columns(4)
            
            with col_conv_moeda:
                usar_conversao_dhl = st.checkbox("💱 Conversão de moeda", value=False, key="usar_conv_dhl")
                taxa_conversao_dhl = st.number_input("Taxa:", 
                                                    min_value=0.01, 
                                                    value=1.0, 
                                                    step=0.01,
                                                    format="%.2f",
                                                    key="taxa_dhl",
                                                    help="Ex: 1.17 para EUR → USD",
                                                    disabled=not usar_conversao_dhl)
            
            with col_margem:
                adicionar_margem_dhl = st.checkbox("📊 Gerar margem", 
                                                  value=True, key="margem_dhl")
            
            with col_incremento:
                incremento_dhl = st.selectbox(
                    "⚖️ Incremento:",
                    options=[0.1, 0.5, 1.0],
                    format_func=lambda x: f"{x} kg ({int(x*1000)}g)",
                    key="incremento_dhl",
                    help="De quanto em quanto o peso aumenta"
                )
            
            with col_conv_peso:
                converter_peso_dhl = st.checkbox("🔄 lb → kg", value=False, key="conv_peso_dhl",
                                                 help="Converte pesos de libras para quilogramas")
            
            
            arquivo_excel_dhl = st.file_uploader("Escolha a planilha DHL", type=["xlsx", "xls"], key="dhl_excel")
            
            if arquivo_excel_dhl:
                if st.button("Processar DHL", key="btn_dhl"):
                    if not nome_cliente_dhl or nome_cliente_dhl.strip() == "":
                        st.error("❌ Por favor, preencha o nome do cliente.")
                    else:
                        with st.spinner("Aguarde... Processando a planilha DHL..."):
                            try:
                                arquivos_gerados = processar_arquivo_excel(
                                    arquivo_excel_dhl, 
                                    transportadora='DHL',
                                    nome_cliente=nome_cliente_dhl.strip(),
                                    adicionar_margem=adicionar_margem_dhl,
                                    taxa_conversao=taxa_conversao_dhl if usar_conversao_dhl else 1.0,
                                    incremento_peso=incremento_dhl,
                                    converter_lb_para_kg=converter_peso_dhl,
                                    gerar_importacao=False,
                                    pais_importacao=None,
                                    iso_importacao=None
                                )
                                if arquivos_gerados:
                                    zip_buffer = io.BytesIO()
                                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
                                        for arquivo in arquivos_gerados:
                                            zf.writestr(arquivo['nome'], arquivo['dados'])
                                    
                                    st.success(f"✅ Planilha processada com sucesso! {len(arquivos_gerados)} arquivos gerados.")
                                    st.download_button(
                                        label="📥 Baixar Todos os Arquivos (.zip)", 
                                        data=zip_buffer.getvalue(),
                                        file_name="resultados_DHL.zip", 
                                        mime="application/zip",
                                        use_container_width=True
                                    )
                                else:
                                    st.warning("Nenhum arquivo foi gerado.")
                            except Exception as e:
                                st.error(f"❌ Ocorreu um erro: {e}")
                                import traceback
                                with st.expander("Detalhes do erro"):
                                    st.code(traceback.format_exc())
    
    # --- MENU EXPANSÍVEL PARA OUTRAS TRANSPORTADORAS ---
    with st.expander("📮 Outras Transportadoras"):
        st.markdown("### Processador Genérico")
        st.info("⚠️ **Atenção:** Esta opção processa qualquer transportadora. Certifique-se de que o arquivo Excel segue o formato padrão.")
        
        # Campos de cliente e transportadora
        col_cliente, col_transp = st.columns(2)
        with col_cliente:
            nome_cliente_outras = st.text_input("Nome do Cliente*:", key="nome_cliente_outras", 
                                               placeholder="Ex: ClienteXYZ")
        with col_transp:
            nome_transportadora_outras = st.text_input("Nome da Transportadora*:", key="nome_transportadora_outras",
                                                      placeholder="Ex: TNT, Aramex, etc.",
                                                      help="Este nome aparecerá nos arquivos gerados")
        
        # Configurações em 4 colunas
        col_conv_moeda, col_margem, col_incremento, col_conv_peso = st.columns(4)
        
        with col_conv_moeda:
            usar_conversao_outras = st.checkbox("💱 Conversão de moeda", value=False, key="usar_conv_outras")
            taxa_conversao_outras = st.number_input("Taxa:", 
                                                   min_value=0.01, 
                                                   value=1.0, 
                                                   step=0.01,
                                                   format="%.2f",
                                                   key="taxa_outras",
                                                   help="Ex: 1.17 para EUR → USD",
                                                   disabled=not usar_conversao_outras)
        
        with col_margem:
            adicionar_margem_outras = st.checkbox("📊 Gerar margem", 
                                                 value=True, key="margem_outras")
        
        with col_incremento:
            incremento_outras = st.selectbox(
                "⚖️ Incremento:",
                options=[0.1, 0.5, 1.0],
                format_func=lambda x: f"{x} kg ({int(x*1000)}g)",
                key="incremento_outras",
                help="De quanto em quanto o peso aumenta"
            )
        
        with col_conv_peso:
            converter_peso_outras = st.checkbox("🔄 lb → kg", value=False, key="conv_peso_outras",
                                               help="Converte pesos de libras para quilogramas")
        
        
        # Upload do arquivo
        arquivo_excel_outras = st.file_uploader("Escolha a planilha da transportadora", 
                                               type=["xlsx", "xls"], key="outras_excel")
        
        if arquivo_excel_outras:
            if st.button("Processar Transportadora", key="btn_outras"):
                if not nome_cliente_outras or nome_cliente_outras.strip() == "":
                    st.error("❌ Por favor, preencha o nome do cliente.")
                elif not nome_transportadora_outras or nome_transportadora_outras.strip() == "":
                    st.error("❌ Por favor, preencha o nome da transportadora.")
                else:
                    with st.spinner("Aguarde... Processando a planilha..."):
                        try:
                            arquivos_gerados = processar_arquivo_excel(
                                arquivo_excel_outras, 
                                transportadora=nome_transportadora_outras.strip().upper(),
                                nome_cliente=nome_cliente_outras.strip(),
                                adicionar_margem=adicionar_margem_outras,
                                taxa_conversao=taxa_conversao_outras if usar_conversao_outras else 1.0,
                                incremento_peso=incremento_outras,
                                converter_lb_para_kg=converter_peso_outras,
                                gerar_importacao=False,
                                pais_importacao=None,
                                iso_importacao=None
                            )
                            if arquivos_gerados:
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
                                    for arquivo in arquivos_gerados:
                                        zf.writestr(arquivo['nome'], arquivo['dados'])
                                
                                st.success(f"✅ Planilha processada com sucesso! {len(arquivos_gerados)} arquivos gerados.")
                                st.download_button(
                                    label="📥 Baixar Todos os Arquivos (.zip)", 
                                    data=zip_buffer.getvalue(),
                                    file_name="resultados_Outras.zip", 
                                    mime="application/zip",
                                    use_container_width=True
                                )
                            else:
                                st.warning("Nenhum arquivo foi gerado.")
                        except Exception as e:
                            st.error(f"❌ Ocorreu um erro: {e}")
                            import traceback
                            with st.expander("Detalhes do erro"):
                                st.code(traceback.format_exc())

elif escolha_topico == "Tabela de Importação":
    st.header("🌍 Tabela de Importação por Zona")
    st.info("Esta ferramenta gera tabelas separadas por zona com um país de destino único.")
    st.markdown("### Como funciona:")
    st.markdown("""
    - Escolha a transportadora e serviço
    - Defina o país de destino (ex: Brazil, Mexico, Chile)
    - O sistema gerará **um arquivo por zona** com todos os preços daquela zona
    - Todos os registros terão o mesmo país de destino que você escolher
    """)
    
    # Seleção da transportadora
    col_transp, col_servico = st.columns(2)
    with col_transp:
        transportadora_import = st.selectbox(
            "Transportadora:",
            ["FEDEX", "UPS", "DHL", "OUTRAS"],
            key="transp_import"
        )
    
    with col_servico:
        if transportadora_import == "FEDEX":
            servicos_opcoes = ["Priority", "Economy", "CP", "Todos"]
        elif transportadora_import == "UPS":
            servicos_opcoes = ["Express", "Standard", "Todos"]
        elif transportadora_import == "DHL":
            servicos_opcoes = ["dhl"]
        else:
            servicos_opcoes = ["Todos"]
        
        servico_import = st.selectbox(
            "Serviço:",
            servicos_opcoes,
            key="servico_import"
        )
    
    # Configurações
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nome_cliente_import = st.text_input(
            "Nome do Cliente*:",
            key="cliente_import",
            placeholder="Ex: ClienteXYZ"
        )
    
    with col2:
        pais_import = st.text_input(
            "País de Destino*:",
            value="Brazil",
            key="pais_import",
            placeholder="Ex: Brazil, Mexico, Chile"
        )
    
    with col3:
        iso_import = st.text_input(
            "Código ISO*:",
            value="BR",
            key="iso_import",
            placeholder="Ex: BR, MX, CL"
        )
    
    # Opções adicionais
    col_moeda, col_peso, col_incremento, col_margem = st.columns(4)
    
    with col_moeda:
        usar_conversao_import = st.checkbox("💱 Conversão de moeda", value=False, key="conv_moeda_import")
        taxa_conversao_import = st.number_input(
            "Taxa:",
            min_value=0.01,
            value=1.0,
            step=0.01,
            format="%.2f",
            key="taxa_import",
            help="Ex: 1.17 para EUR → USD",
            disabled=not usar_conversao_import
        )
    
    with col_peso:
        converter_peso_import = st.checkbox("🔄 lb → kg", value=False, key="conv_peso_import")
    
    with col_incremento:
        incremento_import = st.selectbox(
            "⚖️ Incremento:",
            options=[0.1, 0.5, 1.0],
            format_func=lambda x: f"{x} kg ({int(x*1000)}g)",
            key="incremento_import"
        )
    
    with col_margem:
        adicionar_margem_import = st.checkbox("📊 Gerar margem", value=True, key="margem_import")
    
    # Nome da transportadora se for OUTRAS
    if transportadora_import == "OUTRAS":
        nome_transportadora_import = st.text_input(
            "Nome da Transportadora*:",
            key="nome_transp_import",
            placeholder="Ex: TNT, Aramex, etc."
        )
    
    # Upload do arquivo
    arquivo_excel_import = st.file_uploader(
        "📤 Escolha o arquivo Excel:",
        type=["xlsx", "xls"],
        key="arquivo_import"
    )
    
    if arquivo_excel_import:
        if st.button("🚀 Gerar Tabela de Importação", key="btn_import", use_container_width=True):
            # Validações
            if not nome_cliente_import or nome_cliente_import.strip() == "":
                st.error("❌ Por favor, preencha o nome do cliente.")
            elif not pais_import or pais_import.strip() == "":
                st.error("❌ Por favor, preencha o país de destino.")
            elif not iso_import or iso_import.strip() == "":
                st.error("❌ Por favor, preencha o código ISO.")
            elif transportadora_import == "OUTRAS" and (not nome_transportadora_import or nome_transportadora_import.strip() == ""):
                st.error("❌ Por favor, preencha o nome da transportadora.")
            else:
                with st.spinner(f"Gerando tabela de importação para {pais_import}..."):
                    try:
                        # Prepara lista de serviços
                        if transportadora_import == "FEDEX" and servico_import != "Todos":
                            servicos_filtrar = [servico_import]
                        elif transportadora_import == "UPS" and servico_import != "Todos":
                            servicos_filtrar = [servico_import]
                        else:
                            servicos_filtrar = None
                        
                        # Processa
                        transportadora_final = nome_transportadora_import.strip().upper() if transportadora_import == "OUTRAS" else transportadora_import
                        
                        arquivos_gerados = processar_arquivo_excel(
                            arquivo_excel_import,
                            transportadora=transportadora_final,
                            nome_cliente=nome_cliente_import.strip(),
                            adicionar_margem=adicionar_margem_import,
                            taxa_conversao=taxa_conversao_import if usar_conversao_import else 1.0,
                            incremento_peso=incremento_import,
                            converter_lb_para_kg=converter_peso_import,
                            servicos_filtrar=servicos_filtrar,
                            gerar_importacao=True,
                            pais_importacao=pais_import.strip(),
                            iso_importacao=iso_import.strip()
                        )
                        
                        if arquivos_gerados:
                            # Filtra apenas arquivos de importação (que contêm "Zona" no nome)
                            arquivos_importacao = [arq for arq in arquivos_gerados if "Zona" in arq['nome']]
                            
                            if arquivos_importacao:
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zf:
                                    for arquivo in arquivos_importacao:
                                        zf.writestr(arquivo['nome'], arquivo['dados'])
                                
                                st.success(f"✅ Tabela de importação gerada com sucesso! {len(arquivos_importacao)} arquivos.")
                                st.download_button(
                                    label="📥 Baixar Tabela de Importação (.zip)",
                                    data=zip_buffer.getvalue(),
                                    file_name=f"importacao_{pais_import}_{transportadora_final}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                            else:
                                st.warning("⚠️ Nenhum arquivo de importação foi gerado.")
                        else:
                            st.warning("Nenhum arquivo foi gerado.")
                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro: {e}")
                        import traceback
                        with st.expander("Detalhes do erro"):
                            st.code(traceback.format_exc())
        
elif escolha_topico == "RECOM":
    st.header("Módulo RECOM")
    st.info("Funcionalidade em desenvolvimento...")

elif escolha_topico == "Troquecommerce":
    st.header("Módulo Troquecommerce")
    st.info("Funcionalidade em desenvolvimento...")