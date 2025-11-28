# Nome do arquivo: processador_excel.py

import pandas as pd
import numpy as np
import os
import unidecode
import io
from banco_paises import processar_tabela_com_banco_paises

# --- CONFIGURAÇÕES POR TRANSPORTADORA ---
CONFIGURACOES_TRANSPORTADORAS = {
    'FEDEX': {
        'abas_preco': ['Priority', 'Economy', 'CP'],
        'mapa_abas_zonas': {
            'Priority': 'zones priority ',
            'Economy': 'zones economy',
            'CP': 'zones cp'
        },
        'mapa_zonas_priority': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'T': 5, 'U': 5, 'V': 5, 'W': 5, 'X': 5, 'Y': 5
        },
        'mapa_zonas_economy_cp': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'V': 5, 'W': 5, 'X': 5
        }
    },
    'DHL': {
        'abas_preco': ['dhl'],
        'mapa_abas_zonas': {
            'dhl': 'zonas dhl'
        },
        'mapa_zonas_priority': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'T': 5, 'U': 5, 'V': 5, 'W': 5, 'X': 5, 'Y': 5
        },
        'mapa_zonas_economy_cp': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'V': 5, 'W': 5, 'X': 5
        }
    },
    'UPS': {
        'abas_preco': ['Express', 'Standard'],
        'mapa_abas_zonas': {
            'Express': 'zones express',
            'Standard': 'zones standard'
        },
        'mapa_zonas_priority': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'T': 5, 'U': 5, 'V': 5, 'W': 5, 'X': 5, 'Y': 5
        },
        'mapa_zonas_economy_cp': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'V': 5, 'W': 5, 'X': 5
        }
    },
    'OUTRAS': {
        'abas_preco': ['Servico1', 'Servico2', 'Servico3'],  # Nomes genéricos - serão detectados automaticamente
        'mapa_abas_zonas': {},  # Será preenchido dinamicamente
        'mapa_zonas_priority': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'T': 5, 'U': 5, 'V': 5, 'W': 5, 'X': 5, 'Y': 5
        },
        'mapa_zonas_economy_cp': {
            'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 3, 'G': 3, 'H': 4,
            'I': 4, 'R': 4, 'S': 4, 'V': 5, 'W': 5, 'X': 5
        }
    }
}

# Valores fixos (comuns a todas as transportadoras)
VALORES_FIXOS = {
    'exceeding_price_300': 0,
    'exceeding_price_1000': 0,
    'cubic_weight': 200,
    'fuel_fee_percent': 10,
    'overweight_handling': 331,
    'exceeding_dimensions_handling': 331,
    'remote_area_min': 88,
    'remote_area_by_weight': 1.86,
    'scheduled_delivery_9': 107.5,
    'scheduled_delivery_10': 43,
    'scheduled_delivery_12': 21,
    'insurance_min': 39,
    'insurance_value_percent': 1,
    'doc_protection': 18,
    'max_weight': 300,
    'max_width': 120,
    'max_height': 80,
    'max_length': 80
}


# --- FUNÇÃO PARA ARREDONDAR PESO COMERCIAL ---
def arredondar_peso_comercial(peso):
    """
    Arredonda peso para cima ao meio kg mais próximo (0.5, 1.0, 1.5, 2.0, etc.)
    
    Exemplos:
    0.6 → 1.0
    0.7 → 1.0
    1.1 → 1.5
    1.2 → 1.5
    1.6 → 2.0
    """
    import math
    # Arredonda para cima ao 0.5 mais próximo
    return math.ceil(peso * 2) / 2


# --- FUNÇÃO PARA APLICAR REGRAS INCREMENTAIS ---
def aplicar_regras_incrementais(df_base, regras_incrementais, zonas_disponiveis, incremento_kg=0.1):
    """
    Aplica regras incrementais gerando pesos conforme incremento escolhido (0.1, 0.5 ou 1.0 kg)
    e calculando preço usando o valor incremental por kg baseado no peso comercial.
    
    Args:
        incremento_kg: 0.1 (100g), 0.5 (500g) ou 1.0 (1kg)
    """
    if not regras_incrementais:
        return df_base
    
    novas_linhas_geradas = []
    
    # Define precisão baseada no incremento
    if incremento_kg == 0.1:
        precisao = 1  # Uma casa decimal
    elif incremento_kg == 0.5:
        precisao = 1  # Uma casa decimal
    else:
        precisao = 0  # Sem decimais
    
    for (iso, country, zona_letra), group in df_base.groupby(['iso', 'country', 'Zona_Letra']):
        if group.empty:
            continue
        
        # Pega a última linha da tabela base (maior peso)
        ultima_linha = group.sort_values('range_start', ascending=False).iloc[0]
        ultimo_peso = float(ultima_linha['range_start'])
        ultimo_preco = float(ultima_linha['price'])
        
        for regra in regras_incrementais:
            peso_inicial = float(regra['peso_inicial'])
            peso_final = float(regra['peso_final'])
            valores_por_zona = regra['valores_zona']
            
            if str(zona_letra) not in valores_por_zona:
                continue
            
            valor_incremental_por_kg = float(valores_por_zona[str(zona_letra)])
            peso_gerado = peso_inicial
            
            # Gera pesos conforme o incremento escolhido
            while round(peso_gerado, precisao) <= peso_final:
                # Calcula o peso comercial (arredondado para cima ao 0.5 mais próximo)
                peso_comercial = arredondar_peso_comercial(peso_gerado)
                
                # Calcula quantos kgs foram adicionados (baseado no peso comercial)
                kgs_adicionados = peso_comercial - ultimo_peso
                
                # Calcula o preço: último preço + (kgs adicionados × valor incremental)
                preco_calculado = ultimo_preco + (kgs_adicionados * valor_incremental_por_kg)
                
                # Cria nova linha
                linha_nova = ultima_linha.to_dict()
                linha_nova['range_start'] = round(peso_gerado, precisao)
                linha_nova['range_end'] = round(peso_gerado, precisao)
                linha_nova['price'] = round(preco_calculado, 2)
                
                novas_linhas_geradas.append(linha_nova)
                
                peso_gerado = round(peso_gerado + incremento_kg, precisao)
    
    if novas_linhas_geradas:
        df_novas_linhas = pd.DataFrame(novas_linhas_geradas)
        return pd.concat([df_base, df_novas_linhas], ignore_index=True)
    
    return df_base



# --- FUNÇÃO PARA APLICAR MARGENS E CRIAR ARQUIVOS EM MEMÓRIA ---
def aplicar_margens_e_criar_arquivos_em_memoria(df_base, nome_base_arquivo, adicionar_margem=True):
    """
    Aplica diferentes margens e cria arquivos CSV em memória para cada plano
    
    Args:
        df_base: DataFrame base
        nome_base_arquivo: Nome base para os arquivos
        adicionar_margem: Se True, gera arquivos com margens. Se False, gera apenas arquivo base.
    """
    if df_base.empty:
        return []
    
    arquivos_gerados = []
    
    # Prepara o dataframe base
    df_sem_margem = df_base.copy()
    df_sem_margem['country'] = df_sem_margem['country'].apply(unidecode.unidecode)
    
    # Se NÃO adicionar margem, gera apenas um arquivo
    if not adicionar_margem:
        csv_string = df_sem_margem.to_csv(index=False, sep=';', decimal='.', 
                                         float_format='%.10g', encoding='cp1252')
        arquivos_gerados.append({'nome': f"{nome_base_arquivo}.csv", 'dados': csv_string})
        return arquivos_gerados
    
    # Se adicionar margem, gera todos os arquivos
    csv_string = df_sem_margem.to_csv(index=False, sep=';', decimal='.', 
                                     float_format='%.10g', encoding='cp1252')
    arquivos_gerados.append({'nome': f"{nome_base_arquivo}_Base.csv", 'dados': csv_string})
    
    # Aplica as margens - NOMES SEM A PALAVRA "margem"
    plano = ['Lap', 'Special', 'Partner', 'Pro', 'Scaleup', 'Startup']
    margem = [1, 1.15, 1.2, 1.33, 1.4, 1.7, 1.9]
    colunas_margem = ['price', 'exceeding_price_300', 'exceeding_price_1000']

    for i, nome_plano in enumerate(plano):
        df_margem = df_base.copy()
        df_margem['country'] = df_margem['country'].apply(unidecode.unidecode)
        
        for col in colunas_margem:
            if col in df_margem.columns:
                 df_margem[col] = round((df_margem[col].astype(float) / margem[i]) * margem[i+1], 2)
        
        csv_string = df_margem.to_csv(index=False, sep=';', decimal='.', 
                                     float_format='%.10g', encoding='cp1252')
        # Nome sem "_margem" - apenas o plano direto
        arquivos_gerados.append({'nome': f"{nome_base_arquivo}_{nome_plano}.csv", 'dados': csv_string})
        
    return arquivos_gerados


# --- FUNÇÃO PRINCIPAL DE PROCESSAMENTO ---
def processar_arquivo_excel(arquivo_excel_recebido, transportadora='FEDEX', nome_cliente='', adicionar_margem=True, taxa_conversao=1.0, incremento_peso=0.1, converter_lb_para_kg=False, servicos_filtrar=None, gerar_importacao=False, pais_importacao=None, iso_importacao=None):
    """
    Processa arquivo Excel de tabelas de frete de acordo com a transportadora escolhida
    
    Args:
        arquivo_excel_recebido: Arquivo Excel (pode ser path ou file object)
        transportadora: 'FEDEX', 'UPS', 'DHL', 'OUTRAS', etc.
        nome_cliente: Nome do cliente (opcional) para personalizar nome dos arquivos
        adicionar_margem: Se True, gera arquivos com diferentes margens. Se False, gera apenas arquivo base.
        taxa_conversao: Taxa de conversão de moeda (ex: 1.17 para converter EUR para USD)
        incremento_peso: Incremento de peso em kg (0.1 para 100g, 0.5 para 500g, 1.0 para 1kg)
        converter_lb_para_kg: Se True, converte pesos de libras (lb) para quilogramas (kg)
        servicos_filtrar: Lista de serviços a processar (ex: ['Priority', 'Economy']) ou None para todos
        gerar_importacao: Se True, gera tabela de importação com país único
        pais_importacao: Nome do país de destino para tabela de importação
        iso_importacao: Código ISO do país para tabela de importação
    
    Returns:
        Lista de dicionários com {'nome': nome_arquivo, 'dados': conteudo_csv}
    """
    
    print(f"\nIniciando processamento para {transportadora}...")
    
    # Verifica se a transportadora está configurada, se não usa config genérica
    if transportadora.upper() in CONFIGURACOES_TRANSPORTADORAS:
        config = CONFIGURACOES_TRANSPORTADORAS[transportadora.upper()]
    else:
        # Transportadora não configurada - usa configuração genérica (como "OUTRAS")
        print(f"   - Transportadora '{transportadora}' não pré-configurada. Usando detecção automática.")
        config = CONFIGURACOES_TRANSPORTADORAS['OUTRAS'].copy()
    todos_os_arquivos_finais = []
    
    try:
        xls = pd.ExcelFile(arquivo_excel_recebido)
        print(f"Abas encontradas no arquivo: {xls.sheet_names}")
        
        # Extrai o nome base do arquivo Excel
        if hasattr(arquivo_excel_recebido, 'name'):
            nome_base_excel = os.path.splitext(arquivo_excel_recebido.name)[0]
        else:
            nome_base_excel = os.path.splitext(os.path.basename(str(arquivo_excel_recebido)))[0]
        
        print(f"Nome base do arquivo: {nome_base_excel}")
        
        # Para transportadoras não pré-configuradas, detecta automaticamente as abas
        if transportadora.upper() not in ['FEDEX', 'UPS', 'DHL']:
            # Identifica abas de preço (todas exceto as que contêm "zona" no nome)
            abas_de_preco = [aba for aba in xls.sheet_names if 'zona' not in aba.lower() and 'zone' not in aba.lower()]
            print(f"Abas de preço detectadas automaticamente: {abas_de_preco}")
            
            # Tenta identificar abas de zonas correspondentes
            config['mapa_abas_zonas'] = {}
            for aba_preco in abas_de_preco:
                # Procura por uma aba de zona com nome similar
                for aba_zona in xls.sheet_names:
                    if ('zona' in aba_zona.lower() or 'zone' in aba_zona.lower()):
                        # Usa a primeira aba de zona encontrada como padrão
                        config['mapa_abas_zonas'][aba_preco] = aba_zona
                        break
        else:
            # Processa cada aba de preços conforme configurado
            abas_de_preco = config['abas_preco']

        for nome_da_aba in abas_de_preco:
            # Verifica se a aba existe no arquivo
            if nome_da_aba not in xls.sheet_names:
                print(f"Aviso: Aba '{nome_da_aba}' não encontrada no arquivo. Pulando...")
                continue
            
            # Filtra serviços se especificado (para FEDEX principalmente)
            if servicos_filtrar is not None and nome_da_aba not in servicos_filtrar:
                print(f"Pulando aba '{nome_da_aba}' (não selecionada pelo usuário)")
                continue
                
            print(f"\n--- Processando a aba: '{nome_da_aba}' ---")
            
            # Lê a aba de zonas correspondente
            aba_zona = config['mapa_abas_zonas'][nome_da_aba]
            
            if aba_zona not in xls.sheet_names:
                print(f"Aviso: Aba de zonas '{aba_zona}' não encontrada. Pulando...")
                continue
                
            df_zonas_raw = pd.read_excel(xls, sheet_name=aba_zona, header=0)
            
            # Verifica se tem coluna ISO - se não tiver, usa banco de países
            if len(df_zonas_raw.columns) >= 3:
                # Formato completo: country, iso, zona
                df_zonas = df_zonas_raw.copy()
                df_zonas.columns = ['country', 'iso', 'Zona_Letra']
                print(f"   - Zonas carregadas de: '{aba_zona}' ({len(df_zonas)} países)")
            else:
                # Formato simplificado: apenas country e zona - usa banco de países
                print(f"   - Detectado formato simplificado (sem ISO). Usando banco de países...")
                df_zonas = processar_tabela_com_banco_paises(df_zonas_raw)
                print(f"   - Zonas processadas: {len(df_zonas)} países (ISO adicionado automaticamente)")
            
            # Lê a aba de preços
            df_raw = pd.read_excel(xls, sheet_name=nome_da_aba, header=None)
        
            # A linha 1 contém as zonas (A, B, C, ...)
            zonas_disponiveis_raw = df_raw.iloc[1, 1:].dropna().tolist()
            zonas_disponiveis = [z for z in zonas_disponiveis_raw if z != 'Kgs']
            print(f"   - Zonas de preço encontradas: {zonas_disponiveis}")
            
            # Processa cada seção (Envelope, Pak, Package)
            todas_linhas = []
            regras_incrementais = []
            
            # Identifica as linhas de cada tipo
            idx = 2
            while idx < len(df_raw):
                row = df_raw.iloc[idx]
                tipo_servico = row[0] if pd.notna(row[0]) else row[1]
                
                # Se encontrar uma nova tabela de regras incrementais
                if tipo_servico == 'Weight' and idx > 2:
                    print(f"   - Encontradas regras incrementais na linha {idx}")
                    if idx + 1 < len(df_raw):
                        linha_kgs = df_raw.iloc[idx + 1]
                        
                        if linha_kgs[0] == 'Kgs':
                            zonas_regras = linha_kgs[1:].dropna().tolist()
                            col_offset = 1
                        elif linha_kgs[1] == 'Kgs':
                            zonas_regras = linha_kgs[2:].dropna().tolist()
                            col_offset = 2
                        else:
                            idx += 1
                            continue
                        
                        j = idx + 2
                        while j < len(df_raw):
                            linha_regra = df_raw.iloc[j]
                            peso_info = linha_regra[0]
                            
                            if pd.isna(peso_info):
                                break
                            
                            try:
                                if isinstance(peso_info, str):
                                    if '-' in peso_info:
                                        partes = peso_info.split('-')
                                        peso_inicial = float(partes[0].strip().replace(',', '.'))
                                        peso_final = float(partes[1].strip().replace(',', '.'))
                                        valores_zona = {}
                                        
                                        for i, zona in enumerate(zonas_regras):
                                            valor = linha_regra[i + 1]
                                            if pd.notna(valor):
                                                valor_str = str(valor).replace(',', '.')
                                                valores_zona[str(zona)] = float(valor_str)
                                        
                                        regras_incrementais.append({
                                            'peso_inicial': peso_inicial,
                                            'peso_final': peso_final,
                                            'valores_zona': valores_zona
                                        })
                                    else:
                                        peso_inicial = float(peso_info.replace(',', '.'))
                                        peso_final = float(str(linha_regra[1]).replace(',', '.'))
                                        valores_zona = {}
                                        
                                        for i, zona in enumerate(zonas_regras):
                                            valor = linha_regra[i + col_offset]
                                            if pd.notna(valor):
                                                valor_str = str(valor).replace(',', '.')
                                                valores_zona[str(zona)] = float(valor_str)
                                        
                                        regras_incrementais.append({
                                            'peso_inicial': peso_inicial,
                                            'peso_final': peso_final,
                                            'valores_zona': valores_zona
                                        })
                                else:
                                    peso_inicial = float(peso_info)
                                    peso_final = float(linha_regra[1])
                                    valores_zona = {}
                                    
                                    for i, zona in enumerate(zonas_regras):
                                        valor = linha_regra[i + col_offset]
                                        if pd.notna(valor):
                                            valor_str = str(valor).replace(',', '.')
                                            valores_zona[str(zona)] = float(valor_str)
                                    
                                    regras_incrementais.append({
                                        'peso_inicial': peso_inicial,
                                        'peso_final': peso_final,
                                        'valores_zona': valores_zona
                                    })
                            except Exception as e:
                                print(f"     Erro ao processar regra na linha {j}: {e}")
                                break
                            j += 1
                        break
                    idx += 1
                    continue
                
                # Envelope: só tem uma linha de preço
                if tipo_servico == 'Envelope':
                    peso = 0.5
                    for i, zona_letra in enumerate(zonas_disponiveis):
                        col_idx = i + 2 if 'Kgs' in zonas_disponiveis_raw else i + 1
                        preco = df_raw.iloc[idx + 1, col_idx]
                        if pd.notna(preco):
                            todas_linhas.append({
                                'Tipo': 'Envelope',
                                'range_end': peso,
                                'range_start': peso,
                                'Zona_Letra': zona_letra,
                                'price': preco
                            })
                    idx += 2
                    continue
                
                # Pak e Package: múltiplas linhas de peso
                elif tipo_servico in ['Pak', 'Package']:
                    j = idx + 1
                    while j < len(df_raw):
                        peso_col0 = df_raw.iloc[j, 0]
                        peso_col1 = df_raw.iloc[j, 1]
                        peso = peso_col0 if pd.notna(peso_col0) else peso_col1
                        
                        if pd.isna(peso) or peso in ['Envelope', 'Pak', 'Package', 'Weight']:
                            break
                        
                        try:
                            peso = float(peso)
                            for i, zona_letra in enumerate(zonas_disponiveis):
                                col_idx = i + 2 if 'Kgs' in zonas_disponiveis_raw else i + 1
                                preco = df_raw.iloc[j, col_idx]
                                if pd.notna(preco):
                                    todas_linhas.append({
                                        'Tipo': tipo_servico,
                                        'range_end': peso,
                                        'range_start': peso,
                                        'Zona_Letra': zona_letra,
                                        'price': preco
                                    })
                        except:
                            pass
                        j += 1
                    idx = j
                    continue
                
                idx += 1
            
            print(f"   - Total de regras incrementais encontradas: {len(regras_incrementais)}")
            
            # Cria DataFrame com todos os dados
            df_precos = pd.DataFrame(todas_linhas)
            
            if df_precos.empty:
                print(f"   Nenhum dado encontrado nesta aba. Pulando...")
                continue
            
            # Limpa e converte preços
            df_precos['price'] = pd.to_numeric(
                df_precos['price'].astype(str).str.replace(',', '.'), 
                errors='coerce'
            )
            df_precos.dropna(subset=['price'], inplace=True)
            
            # Aplica conversão de peso de lb para kg se necessário
            if converter_lb_para_kg:
                print("   - Convertendo pesos de libras (lb) para quilogramas (kg)...")
                fator_conversao_lb_para_kg = 0.453592
                df_precos['range_start'] = (df_precos['range_start'] * fator_conversao_lb_para_kg).round(1)
                df_precos['range_end'] = (df_precos['range_end'] * fator_conversao_lb_para_kg).round(1)
            
            # Aplica conversão de moeda se necessário
            if taxa_conversao != 1.0:
                print(f"   - Aplicando taxa de conversão de moeda: {taxa_conversao}")
                df_precos['price'] = df_precos['price'] * taxa_conversao
            
            df_precos['price'] = df_precos['price'].round(2)
            
            # Faz merge com as zonas
            df_final = pd.merge(df_precos, df_zonas, on='Zona_Letra', how='left')
            
            # Aplica o mapeamento de zona apropriado (1-5)
            if nome_da_aba == 'Priority' or nome_da_aba == 'Express':
                df_final['zone'] = df_final['Zona_Letra'].map(config['mapa_zonas_priority'])
            else:
                df_final['zone'] = df_final['Zona_Letra'].map(config['mapa_zonas_economy_cp'])
            
            df_final['zone'] = df_final['zone'].fillna(5).astype(int)
            
            # Adiciona valores fixos
            for col_name, value in VALORES_FIXOS.items():
                df_final[col_name] = value
            
            # Organiza as colunas
            ordem_colunas = ['iso', 'country', 'zone', 'range_end', 'price'] + list(VALORES_FIXOS.keys())
            df_final = df_final.reindex(columns=ordem_colunas + ['Tipo', 'range_start', 'Zona_Letra'])
            
            # Remove linhas sem país/iso
            df_final.dropna(subset=['iso', 'country'], inplace=True)
            
            print(f"   - Total de registros processados: {len(df_final)}")
            
            # Separa documentos e não-documentos
            if nome_da_aba == 'Priority':
                tabela_doc_final = df_final[df_final['Tipo'] == 'Pak'].copy()
            else:
                tabela_doc_final = df_final[df_final['Tipo'].isin(['Envelope', 'Pak'])].copy()
            
            tabela_not_doc_final_pre = df_final[df_final['Tipo'] == 'Package'].copy()
            
            # Aplica regras incrementais com o incremento escolhido
            if regras_incrementais:
                # Se precisar converter de lb para kg, converte os pesos das regras incrementais também
                if converter_lb_para_kg:
                    print("   - Convertendo pesos das regras incrementais de lb para kg...")
                    fator_conversao_lb_para_kg = 0.453592
                    # Define precisão baseada no incremento
                    if incremento_peso == 1.0:
                        precisao_conversao = 0  # Sem decimais para incremento de 1kg
                    else:
                        precisao_conversao = 1  # Uma casa decimal para 0.1 e 0.5 kg
                    
                    for regra in regras_incrementais:
                        regra['peso_inicial'] = round(regra['peso_inicial'] * fator_conversao_lb_para_kg, precisao_conversao)
                        regra['peso_final'] = round(regra['peso_final'] * fator_conversao_lb_para_kg, precisao_conversao)
                
                if incremento_peso == 0.1:
                    print("   - Aplicando regras incrementais (a cada 100g = 0.1 kg)...")
                elif incremento_peso == 0.5:
                    print("   - Aplicando regras incrementais (a cada 500g = 0.5 kg)...")
                else:
                    print(f"   - Aplicando regras incrementais (a cada {incremento_peso} kg)...")
                print("   - Preços baseados no peso comercial arredondado para cima (0.5, 1.0, 1.5, 2.0...)")
                tabela_not_doc_final = aplicar_regras_incrementais(
                    tabela_not_doc_final_pre, regras_incrementais, zonas_disponiveis, incremento_kg=incremento_peso
                )
            else:
                tabela_not_doc_final = tabela_not_doc_final_pre
            
            # Ordena os dados
            tabela_doc_final.sort_values(by=['country', 'range_end'], inplace=True)
            tabela_not_doc_final.sort_values(by=['country', 'range_end'], inplace=True)
            
            # Remove colunas auxiliares
            tabela_doc_final.drop(columns=['Tipo', 'range_start', 'Zona_Letra'], inplace=True, errors='ignore')
            tabela_not_doc_final.drop(columns=['Tipo', 'range_start', 'Zona_Letra'], inplace=True, errors='ignore')
            
            # Define nomes base para os arquivos seguindo o novo padrão
            # Formato: [nome_cliente_]doc_[transportadora]Table_[NomeAba] ou [nome_cliente_]notDoc_[transportadora]Table_[NomeAba]
            prefixo_cliente = f"{nome_cliente}_" if nome_cliente else ""
            
            transportadora_lower = transportadora.lower()
            nome_aba_limpo = nome_da_aba.replace(' ', '_')
            caminho_base_doc = f"{prefixo_cliente}doc_{transportadora_lower}Table_{nome_aba_limpo}"
            caminho_base_not_doc = f"{prefixo_cliente}notDoc_{transportadora_lower}Table_{nome_aba_limpo}"
            
            # Gera arquivos com ou sem margens
            if adicionar_margem:
                print("   - Aplicando margens e criando arquivos 'docTable'...")
            else:
                print("   - Criando arquivos 'docTable' (sem margem)...")
            
            arquivos_doc = aplicar_margens_e_criar_arquivos_em_memoria(tabela_doc_final, caminho_base_doc, adicionar_margem)
            todos_os_arquivos_finais.extend(arquivos_doc)
            
            if adicionar_margem:
                print("   - Aplicando margens e criando arquivos 'notDocTable'...")
            else:
                print("   - Criando arquivos 'notDocTable' (sem margem)...")
                
            arquivos_not_doc = aplicar_margens_e_criar_arquivos_em_memoria(tabela_not_doc_final, caminho_base_not_doc, adicionar_margem)
            todos_os_arquivos_finais.extend(arquivos_not_doc)
            
            # Gera tabela de importação se solicitado
            if gerar_importacao and pais_importacao and iso_importacao:
                print(f"\n   - Gerando tabela de importação para {pais_importacao} ({iso_importacao})...")
                
                # Cria tabela de importação para doc
                tabela_import_doc = tabela_doc_final.copy()
                tabela_import_doc['country'] = pais_importacao
                tabela_import_doc['iso'] = iso_importacao
                
                caminho_base_import_doc = f"{nome_cliente_limpo}doc_{transportadora_lower}Table_{nome_aba_limpo}_Import"
                arquivos_import_doc = aplicar_margens_e_criar_arquivos_em_memoria(tabela_import_doc, caminho_base_import_doc, adicionar_margem)
                todos_os_arquivos_finais.extend(arquivos_import_doc)
                
                # Cria tabela de importação para notDoc
                tabela_import_not_doc = tabela_not_doc_final.copy()
                tabela_import_not_doc['country'] = pais_importacao
                tabela_import_not_doc['iso'] = iso_importacao
                
                caminho_base_import_not_doc = f"{nome_cliente_limpo}notDoc_{transportadora_lower}Table_{nome_aba_limpo}_Import"
                arquivos_import_not_doc = aplicar_margens_e_criar_arquivos_em_memoria(tabela_import_not_doc, caminho_base_import_not_doc, adicionar_margem)
                todos_os_arquivos_finais.extend(arquivos_import_not_doc)
                
                print(f"   - Tabela de importação gerada: {len(tabela_import_doc)} registros (doc), {len(tabela_import_not_doc)} registros (notDoc)")
            
            print(f"\n   [OK] Aba '{nome_da_aba}' processada com sucesso!")
            print(f"   - Documentos: {len(tabela_doc_final)} registros")
            print(f"   - Não-Documentos: {len(tabela_not_doc_final)} registros")
        
            print("\n" + "="*60)
            print(f"[OK] PROCESSAMENTO DE {transportadora} CONCLUÍDO COM SUCESSO!")
            print(f"Total de arquivos gerados: {len(todos_os_arquivos_finais)}")
            print("="*60)
        
        return todos_os_arquivos_finais
    
    except FileNotFoundError:
        print(f"ERRO: O arquivo não foi encontrado")
        raise
    except Exception as e:
        import traceback
        print(f"\nOcorreu um erro inesperado: {e}")
        traceback.print_exc()
        raise
