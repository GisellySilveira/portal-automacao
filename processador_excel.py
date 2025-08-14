# Nome do arquivo: processador_excel.py

import pandas as pd
import numpy as np
import os
import unidecode

# --- FUNÇÕES DE SUPORTE ---
def aplicar_margens_e_salvar(df_base, caminho_base_arquivo):
    if df_base.empty: return
    plano = ['Lap', 'Special', 'Partner', 'Pro', 'Scaleup', 'Startup']
    margem = [1, 1.15, 1.2, 1.33, 1.4, 1.7, 1.9]
    colunas_margem = ['price', 'exceeding_price_300', 'exceeding_price_1000']
    for i, nome_plano in enumerate(plano):
        df_margem = df_base.copy()
        df_margem['country'] = df_margem['country'].apply(unidecode.unidecode)
        for col in colunas_margem:
            if col in df_margem.columns:
                 df_margem[col] = round((df_margem[col].astype(float) / margem[i]) * margem[i+1], 2)
        caminho_final_csv = f"{caminho_base_arquivo}_{nome_plano}.csv"
        df_margem.to_csv(caminho_final_csv, index=False, sep=';', decimal='.', float_format='%.10g', encoding='cp1252')
        print(f"   -> Arquivo com margem salvo: {os.path.basename(caminho_final_csv)}")

def expandir_pesos_pacote(df_pacote):
    df_pacote_base = df_pacote[df_pacote['range_start'] < 100].copy()
    regras_incremental = df_pacote[df_pacote['range_start'] >= 100].copy()
    novas_linhas_geradas = []
    for (iso, country, zone), group in df_pacote_base.groupby(['iso', 'country', 'zone']):
        if group.empty: continue
        preco_base_99_lbs = group.sort_values('range_start', ascending=False).iloc[0]['price']
        regra_100 = regras_incremental[(regras_incremental['iso'] == iso) & (regras_incremental['zone'] == zone) & (regras_incremental['range_start'] == 100)]
        preco_calculado_150_lbs = None
        if not regra_100.empty:
            preco_adicional_lb = regra_100.iloc[0]['price']
            for peso_atual_lbs in range(100, 151):
                preco_calculado = preco_base_99_lbs + ((peso_atual_lbs - 99) * preco_adicional_lb)
                linha_base = group.iloc[0].to_dict()
                linha_base.update({'range_start': peso_atual_lbs, 'range_end': peso_atual_lbs, 'price': round(preco_calculado, 2)})
                novas_linhas_geradas.append(linha_base)
            preco_calculado_150_lbs = novas_linhas_geradas[-1]['price']
        regra_151 = regras_incremental[(regras_incremental['iso'] == iso) & (regras_incremental['zone'] == zone) & (regras_incremental['range_start'] == 151)]
        if not regra_151.empty and preco_calculado_150_lbs is not None:
            preco_adicional_lb = regra_151.iloc[0]['price']
            for peso_atual_lbs in range(151, 301):
                preco_calculado = preco_calculado_150_lbs + ((peso_atual_lbs - 150) * preco_adicional_lb)
                linha_base = group.iloc[0].to_dict()
                linha_base.update({'range_start': peso_atual_lbs, 'range_end': peso_atual_lbs, 'price': round(preco_calculado, 2)})
                novas_linhas_geradas.append(linha_base)
    if novas_linhas_geradas:
        df_novas_linhas = pd.DataFrame(novas_linhas_geradas)
        return pd.concat([df_pacote_base, df_novas_linhas], ignore_index=True)
    return df_pacote_base

def processar_secao(df, start_row, end_row, tipo, colunas):
    secao = df.iloc[start_row:end_row].copy()
    secao.columns = colunas
    secao['Tipo'] = tipo
    return secao

# --- A FUNÇÃO PRINCIPAL QUE O NOSSO SITE VAI CHAMAR ---
def processar_arquivo_excel(caminho_do_excel_para_processar, pasta_final_para_salvar):
    
    print(f"Iniciando o processamento do arquivo: {os.path.basename(caminho_do_excel_para_processar)}")
    
    # --- NOSSO CÓDIGO COMPLETO E FUNCIONAL DO EXCEL ENTRA AQUI ---
    LBS_TO_KG = 0.45359237
    mapa_zonas_letra_para_numero = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 8, 'J': 9, 'K': 9, 'L': 9, 'M': 9, 'N': 9, 'O': 9}
    valores_fixos = {'exceeding_price_300': 0, 'exceeding_price_1000': 0, 'cubic_weight': 200, 'fuel_fee_percent': 10, 'overweight_handling': 331, 'exceeding_dimensions_handling': 331, 'remote_area_min': 88, 'remote_area_by_weight': 1.86, 'scheduled_delivery_9': 107.5, 'scheduled_delivery_10': 43, 'scheduled_delivery_12': 21, 'insurance_min': 39, 'insurance_value_percent': 1, 'doc_protection': 18, 'max_weight': 300, 'max_width': 120, 'max_height': 80, 'max_length': 80}

    xls = pd.ExcelFile(caminho_do_excel_para_processar)
    df_zonas = pd.read_excel(xls, sheet_name='Zonas', header=0)
    df_zonas_mapeada = df_zonas[['Country/Territory', 'IATA', 'IPE']].copy()
    df_zonas_mapeada.rename(columns={'Country/Territory': 'country', 'IATA': 'iso', 'IPE': 'Zona_Letra'}, inplace=True)
    
    abas_de_preco = [aba for aba in xls.sheet_names if aba != 'Zonas']
    
    for nome_da_aba in abas_de_preco:
        print(f"\n--- Processando a aba: '{nome_da_aba}' ---")
        df_raw = pd.read_excel(xls, sheet_name=nome_da_aba, header=None)
        secoes_info = [{'tipo': t, 'idx': r[1].index[0]} for t in ['Envelope', 'Pak', 'Pacote'] if not (r := df_raw[df_raw[1] == t]).empty]
        if not secoes_info: continue
        secoes_info_sorted = sorted(secoes_info, key=lambda x: x['idx'])
        colunas = df_raw.iloc[secoes_info_sorted[0]['idx'] - 1].fillna('Temp_Col')
        lista_df_secoes = [processar_secao(df_raw, s['idx'] + 1, secoes_info_sorted[i+1]['idx'] if i + 1 < len(secoes_info_sorted) else len(df_raw), s['tipo'], colunas) for i, s in enumerate(secoes_info_sorted)]
        df_precos = pd.concat(lista_df_secoes, ignore_index=True)
        df_precos.columns = df_precos.columns.str.strip()
        df_precos.rename(columns={df_precos.columns[0]: 'range_start', 'Kg': 'range_end'}, inplace=True)
        df_precos['range_start'] = pd.to_numeric(df_precos['range_start'], errors='coerce')
        df_precos['range_end'] = pd.to_numeric(df_precos['range_end'], errors='coerce')
        df_precos['range_start'].fillna(df_precos['range_end'], inplace=True)
        df_precos.dropna(subset=['range_end'], inplace=True)
        id_vars_reais = ['range_start', 'range_end', df_precos.columns[-1]] 
        zone_cols = [col for col in 'ABCDEFGHIJKLMNO']
        df_long = pd.melt(df_precos, id_vars=id_vars_reais, value_vars=zone_cols, var_name='Zona_Letra', value_name='price')
        df_long['price'] = pd.to_numeric(df_long['price'].astype(str).str.replace(',', '.'), errors='coerce')
        df_long.dropna(subset=['price'], inplace=True)
        df_final = pd.merge(df_long, df_zonas_mapeada, on='Zona_Letra', how='left')
        df_final['zone'] = df_final['Zona_Letra'].map(mapa_zonas_letra_para_numero)
        for col_name, value in valores_fixos.items():
            df_final[col_name] = value
        tipo_col_name = id_vars_reais[2]
        ordem_colunas = ['iso', 'country', 'zone', 'range_end', 'price'] + list(valores_fixos.keys())
        df_final = df_final.reindex(columns=ordem_colunas + [tipo_col_name, 'range_start'])
        df_final.dropna(subset=['iso', 'country'], inplace=True)
        
        tabela_doc_final = df_final[df_final[tipo_col_name].isin(['Envelope', 'Pak'])].copy()
        tabela_not_doc_final_pre = df_final[df_final[tipo_col_name] == 'Pacote'].copy()
        tabela_not_doc_final = expandir_pesos_pacote(tabela_not_doc_final_pre)

        tabela_doc_final['range_end'] = round(tabela_doc_final['range_end'] * LBS_TO_KG, 2)
        tabela_not_doc_final['range_end'] = round(tabela_not_doc_final['range_end'] * LBS_TO_KG, 2)

        tabela_doc_final.sort_values(by=['country', 'range_end'], inplace=True)
        tabela_not_doc_final.sort_values(by=['country', 'range_end'], inplace=True)
        
        tabela_doc_final.drop(columns=[tipo_col_name, 'range_start'], inplace=True, errors='ignore')
        tabela_not_doc_final.drop(columns=[tipo_col_name, 'range_start'], inplace=True, errors='ignore')
        
        nome_base_arquivo = nome_da_aba.replace(' ', '_')
        nova_pasta_para_aba = os.path.join(pasta_final_para_salvar, nome_base_arquivo)
        os.makedirs(nova_pasta_para_aba, exist_ok=True)
        
        caminho_base_doc = os.path.join(nova_pasta_para_aba, f"{nome_base_arquivo}_doc")
        caminho_base_not_doc = os.path.join(nova_pasta_para_aba, f"{nome_base_arquivo}_notDoc")

        print(f"   - Salvando arquivos para a aba '{nome_da_aba}'...")
        aplicar_margens_e_salvar(tabela_doc_final, caminho_base_doc)
        aplicar_margens_e_salvar(tabela_not_doc_final, caminho_base_not_doc)
    
    return pasta_final_para_salvar