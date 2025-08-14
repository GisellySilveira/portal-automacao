# Nome do arquivo: processador_excel.py

import pandas as pd
import numpy as np
import os
import unidecode

# --- FUNÇÃO DE SUPORTE MODIFICADA ---
def aplicar_margens_e_criar_arquivos_em_memoria(df_base, nome_base_arquivo):
    """
    Esta função aplica as margens e retorna uma lista de arquivos (nome, dados) em memória.
    Ela NÃO salva mais nada no disco.
    """
    if df_base.empty: return []
    
    arquivos_gerados = []
    plano = ['Lap', 'Special', 'Partner', 'Pro', 'Scaleup', 'Startup']
    margem = [1, 1.15, 1.2, 1.33, 1.4, 1.7, 1.9]
    colunas_margem = ['price', 'exceeding_price_300', 'exceeding_price_1000']

    for i, nome_plano in enumerate(plano):
        df_margem = df_base.copy()
        df_margem['country'] = df_margem['country'].apply(unidecode.unidecode)
        for col in colunas_margem:
            if col in df_margem.columns:
                 df_margem[col] = round((df_margem[col].astype(float) / margem[i]) * margem[i+1], 2)
        
        # Gera o CSV como uma string de texto em memória
        csv_string = df_margem.to_csv(index=False, sep=';', decimal='.', float_format='%.10g', encoding='cp1252')
        
        nome_final_arquivo = f"{nome_base_arquivo}_{nome_plano}.csv"
        # Adiciona o nome e o conteúdo do arquivo à nossa lista
        arquivos_gerados.append({'nome': nome_final_arquivo, 'dados': csv_string})
        
    return arquivos_gerados


# --- FUNÇÃO PRINCIPAL MODIFICADA ---
def processar_arquivo_excel(arquivo_excel_recebido):
    
    # --- TODO O SEU CÓDIGO DE PROCESSAMENTO DO EXCEL VEM AQUI ---
    # A lógica é a mesma, mas agora ele retorna uma lista de arquivos no final

    LBS_TO_KG = 0.45359237
    mapa_zonas_letra_para_numero = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 8, 'J': 9, 'K': 9, 'L': 9, 'M': 9, 'N': 9, 'O': 9}
    valores_fixos = {'exceeding_price_300': 0, 'exceeding_price_1000': 0, 'cubic_weight': 200, 'fuel_fee_percent': 10, 'overweight_handling': 331, 'exceeding_dimensions_handling': 331, 'remote_area_min': 88, 'remote_area_by_weight': 1.86, 'scheduled_delivery_9': 107.5, 'scheduled_delivery_10': 43, 'scheduled_delivery_12': 21, 'insurance_min': 39, 'insurance_value_percent': 1, 'doc_protection': 18, 'max_weight': 300, 'max_width': 120, 'max_height': 80, 'max_length': 80}

    xls = pd.ExcelFile(arquivo_excel_recebido)
    df_zonas = pd.read_excel(xls, sheet_name='Zonas', header=0)
    df_zonas_mapeada = df_zonas[['Country/Territory', 'IATA', 'IPE']].copy()
    df_zonas_mapeada.rename(columns={'Country/Territory': 'country', 'IATA': 'iso', 'IPE': 'Zona_Letra'}, inplace=True)
    
    abas_de_preco = [aba for aba in xls.sheet_names if aba != 'Zonas']
    
    todos_os_arquivos_finais = []

    for nome_da_aba in abas_de_preco:
        print(f"\n--- Processando a aba: '{nome_da_aba}' ---")
        df_raw = pd.read_excel(xls, sheet_name=nome_da_aba, header=None)
        
        # ... (Toda a sua lógica de extração e processamento da aba continua aqui) ...
        # ... (Eu omiti por brevidade, mas ela deve estar aqui) ...
        
        # Exemplo simplificado da lógica de processamento
        df_precos = pd.read_excel(xls, sheet_name=nome_da_aba, header=2) # Simplificação
        df_precos.columns = df_precos.columns.str.strip()
        tabela_doc_final = df_precos.head(10).copy() # Apenas para exemplo
        tabela_doc_final['country'] = "Exemplo" # Adiciona a coluna para a função de margem funcionar
        tabela_not_doc_final = df_precos.tail(10).copy() # Apenas para exemplo
        tabela_not_doc_final['country'] = "Exemplo" # Adiciona a coluna para a função de margem funcionar
        
        # --- PARTE FINAL MODIFICADA ---
        nome_base_arquivo = nome_da_aba.replace(' ', '_')
        caminho_base_doc = f"{nome_base_arquivo}_doc"
        caminho_base_not_doc = f"{nome_base_arquivo}_notDoc"

        lista_arquivos_doc = aplicar_margens_e_criar_arquivos_em_memoria(tabela_doc_final, caminho_base_doc)
        lista_arquivos_not_doc = aplicar_margens_e_criar_arquivos_em_memoria(tabela_not_doc_final, caminho_base_not_doc)
        
        todos_os_arquivos_finais.extend(lista_arquivos_doc)
        todos_os_arquivos_finais.extend(lista_arquivos_not_doc)
    
    # A função principal agora retorna a lista com todos os arquivos
    return todos_os_arquivos_finais