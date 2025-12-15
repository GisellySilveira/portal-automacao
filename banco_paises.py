"""
Banco de dados de países com nomes em Português, Inglês e Espanhol + ISO2
Suporta busca flexível por parte do nome ou fuzzy matching
"""
from difflib import get_close_matches
import unicodedata

PAISES_DATABASE = {
    # ISO2: [Nome_EN, Nome_PT, Nome_ES]
    'AF': ['Afghanistan', 'Afeganistão', 'Afganistán'],
    'AL': ['Albania', 'Albânia', 'Albania'],
    'DZ': ['Algeria', 'Argélia', 'Argelia'],
    'AD': ['Andorra', 'Andorra', 'Andorra'],
    'AO': ['Angola', 'Angola', 'Angola'],
    'AR': ['Argentina', 'Argentina', 'Argentina'],
    'AM': ['Armenia', 'Armênia', 'Armenia'],
    'AU': ['Australia', 'Austrália', 'Australia'],
    'AT': ['Austria', 'Áustria', 'Austria'],
    'AZ': ['Azerbaijan', 'Azerbaijão', 'Azerbaiyán'],
    'BS': ['Bahamas', 'Bahamas', 'Bahamas'],
    'BH': ['Bahrain', 'Bahrein', 'Baréin'],
    'BD': ['Bangladesh', 'Bangladesh', 'Bangladés'],
    'BB': ['Barbados', 'Barbados', 'Barbados'],
    'BY': ['Belarus', 'Belarus', 'Bielorrusia'],
    'BE': ['Belgium', 'Bélgica', 'Bélgica'],
    'BZ': ['Belize', 'Belize', 'Belice'],
    'BJ': ['Benin', 'Benim', 'Benín'],
    'BT': ['Bhutan', 'Butão', 'Bután'],
    'BO': ['Bolivia', 'Bolívia', 'Bolivia'],
    'BA': ['Bosnia and Herzegovina', 'Bósnia e Herzegovina', 'Bosnia y Herzegovina'],
    'BW': ['Botswana', 'Botsuana', 'Botsuana'],
    'BR': ['Brazil', 'Brasil', 'Brasil'],
    'BN': ['Brunei', 'Brunei', 'Brunéi'],
    'BG': ['Bulgaria', 'Bulgária', 'Bulgaria'],
    'BF': ['Burkina Faso', 'Burkina Faso', 'Burkina Faso'],
    'BI': ['Burundi', 'Burundi', 'Burundi'],
    'KH': ['Cambodia', 'Camboja', 'Camboya'],
    'CM': ['Cameroon', 'Camarões', 'Camerún'],
    'CA': ['Canada', 'Canadá', 'Canadá'],
    'CV': ['Cape Verde', 'Cabo Verde', 'Cabo Verde'],
    'CF': ['Central African Republic', 'República Centro-Africana', 'República Centroafricana'],
    'TD': ['Chad', 'Chade', 'Chad'],
    'CL': ['Chile', 'Chile', 'Chile'],
    'CN': ['China', 'China', 'China'],
    'CO': ['Colombia', 'Colômbia', 'Colombia'],
    'KM': ['Comoros', 'Comores', 'Comoras'],
    'CG': ['Congo', 'Congo', 'Congo'],
    'CR': ['Costa Rica', 'Costa Rica', 'Costa Rica'],
    'HR': ['Croatia', 'Croácia', 'Croacia'],
    'CU': ['Cuba', 'Cuba', 'Cuba'],
    'CY': ['Cyprus', 'Chipre', 'Chipre'],
    'CZ': ['Czech Republic', 'República Tcheca', 'República Checa'],
    'DK': ['Denmark', 'Dinamarca', 'Dinamarca'],
    'DJ': ['Djibouti', 'Djibuti', 'Yibuti'],
    'DM': ['Dominica', 'Dominica', 'Dominica'],
    'DO': ['Dominican Republic', 'República Dominicana', 'República Dominicana'],
    'EC': ['Ecuador', 'Equador', 'Ecuador'],
    'EG': ['Egypt', 'Egito', 'Egipto'],
    'SV': ['El Salvador', 'El Salvador', 'El Salvador'],
    'GQ': ['Equatorial Guinea', 'Guiné Equatorial', 'Guinea Ecuatorial'],
    'ER': ['Eritrea', 'Eritreia', 'Eritrea'],
    'EE': ['Estonia', 'Estônia', 'Estonia'],
    'ET': ['Ethiopia', 'Etiópia', 'Etiopía'],
    'FJ': ['Fiji', 'Fiji', 'Fiyi'],
    'FI': ['Finland', 'Finlândia', 'Finlandia'],
    'FR': ['France', 'França', 'Francia'],
    'GA': ['Gabon', 'Gabão', 'Gabón'],
    'GM': ['Gambia', 'Gâmbia', 'Gambia'],
    'GE': ['Georgia', 'Geórgia', 'Georgia'],
    'DE': ['Germany', 'Alemanha', 'Alemania'],
    'GH': ['Ghana', 'Gana', 'Ghana'],
    'GR': ['Greece', 'Grécia', 'Grecia'],
    'GD': ['Grenada', 'Granada', 'Granada'],
    'GT': ['Guatemala', 'Guatemala', 'Guatemala'],
    'GN': ['Guinea', 'Guiné', 'Guinea'],
    'GW': ['Guinea-Bissau', 'Guiné-Bissau', 'Guinea-Bisáu'],
    'GY': ['Guyana', 'Guiana', 'Guyana'],
    'HT': ['Haiti', 'Haiti', 'Haití'],
    'HN': ['Honduras', 'Honduras', 'Honduras'],
    'HK': ['Hong Kong', 'Hong Kong', 'Hong Kong'],
    'HU': ['Hungary', 'Hungria', 'Hungría'],
    'IS': ['Iceland', 'Islândia', 'Islandia'],
    'IN': ['India', 'Índia', 'India'],
    'ID': ['Indonesia', 'Indonésia', 'Indonesia'],
    'IR': ['Iran', 'Irã', 'Irán'],
    'IQ': ['Iraq', 'Iraque', 'Irak'],
    'IE': ['Ireland', 'Irlanda', 'Irlanda'],
    'IL': ['Israel', 'Israel', 'Israel'],
    'IT': ['Italy', 'Itália', 'Italia'],
    'CI': ['Ivory Coast', 'Costa do Marfim', 'Costa de Marfil'],
    'JM': ['Jamaica', 'Jamaica', 'Jamaica'],
    'JP': ['Japan', 'Japão', 'Japón'],
    'JO': ['Jordan', 'Jordânia', 'Jordania'],
    'KZ': ['Kazakhstan', 'Cazaquistão', 'Kazajistán'],
    'KE': ['Kenya', 'Quênia', 'Kenia'],
    'KI': ['Kiribati', 'Kiribati', 'Kiribati'],
    'KW': ['Kuwait', 'Kuwait', 'Kuwait'],
    'KG': ['Kyrgyzstan', 'Quirguistão', 'Kirguistán'],
    'LA': ['Laos', 'Laos', 'Laos'],
    'LV': ['Latvia', 'Letônia', 'Letonia'],
    'LB': ['Lebanon', 'Líbano', 'Líbano'],
    'LS': ['Lesotho', 'Lesoto', 'Lesoto'],
    'LR': ['Liberia', 'Libéria', 'Liberia'],
    'LY': ['Libya', 'Líbia', 'Libia'],
    'LI': ['Liechtenstein', 'Liechtenstein', 'Liechtenstein'],
    'LT': ['Lithuania', 'Lituânia', 'Lituania'],
    'LU': ['Luxembourg', 'Luxemburgo', 'Luxemburgo'],
    'MO': ['Macau', 'Macau', 'Macao'],
    'MK': ['Macedonia', 'Macedônia', 'Macedonia'],
    'MG': ['Madagascar', 'Madagascar', 'Madagascar'],
    'MW': ['Malawi', 'Malawi', 'Malaui'],
    'MY': ['Malaysia', 'Malásia', 'Malasia'],
    'MV': ['Maldives', 'Maldivas', 'Maldivas'],
    'ML': ['Mali', 'Mali', 'Malí'],
    'MT': ['Malta', 'Malta', 'Malta'],
    'MH': ['Marshall Islands', 'Ilhas Marshall', 'Islas Marshall'],
    'MR': ['Mauritania', 'Mauritânia', 'Mauritania'],
    'MU': ['Mauritius', 'Maurício', 'Mauricio'],
    'MX': ['Mexico', 'México', 'México'],
    'FM': ['Micronesia', 'Micronésia', 'Micronesia'],
    'MD': ['Moldova', 'Moldávia', 'Moldavia'],
    'MC': ['Monaco', 'Mônaco', 'Mónaco'],
    'MN': ['Mongolia', 'Mongólia', 'Mongolia'],
    'ME': ['Montenegro', 'Montenegro', 'Montenegro'],
    'MA': ['Morocco', 'Marrocos', 'Marruecos'],
    'MZ': ['Mozambique', 'Moçambique', 'Mozambique'],
    'MM': ['Myanmar', 'Mianmar', 'Birmania'],
    'NA': ['Namibia', 'Namíbia', 'Namibia'],
    'NR': ['Nauru', 'Nauru', 'Nauru'],
    'NP': ['Nepal', 'Nepal', 'Nepal'],
    'NL': ['Netherlands', 'Holanda', 'Países Bajos'],
    'NZ': ['New Zealand', 'Nova Zelândia', 'Nueva Zelanda'],
    'NI': ['Nicaragua', 'Nicarágua', 'Nicaragua'],
    'NE': ['Niger', 'Níger', 'Níger'],
    'NG': ['Nigeria', 'Nigéria', 'Nigeria'],
    'KP': ['North Korea', 'Coreia do Norte', 'Corea del Norte'],
    'NO': ['Norway', 'Noruega', 'Noruega'],
    'OM': ['Oman', 'Omã', 'Omán'],
    'PK': ['Pakistan', 'Paquistão', 'Pakistán'],
    'PW': ['Palau', 'Palau', 'Palaos'],
    'PS': ['Palestine', 'Palestina', 'Palestina'],
    'PA': ['Panama', 'Panamá', 'Panamá'],
    'PG': ['Papua New Guinea', 'Papua-Nova Guiné', 'Papúa Nueva Guinea'],
    'PY': ['Paraguay', 'Paraguai', 'Paraguay'],
    'PE': ['Peru', 'Peru', 'Perú'],
    'PH': ['Philippines', 'Filipinas', 'Filipinas'],
    'PL': ['Poland', 'Polônia', 'Polonia'],
    'PT': ['Portugal', 'Portugal', 'Portugal'],
    'PR': ['Puerto Rico', 'Porto Rico', 'Puerto Rico'],
    'QA': ['Qatar', 'Catar', 'Catar'],
    'RO': ['Romania', 'Romênia', 'Rumania'],
    'RU': ['Russia', 'Rússia', 'Rusia'],
    'RW': ['Rwanda', 'Ruanda', 'Ruanda'],
    'KN': ['Saint Kitts and Nevis', 'São Cristóvão e Nevis', 'San Cristóbal y Nieves'],
    'LC': ['Saint Lucia', 'Santa Lúcia', 'Santa Lucía'],
    'VC': ['Saint Vincent and the Grenadines', 'São Vicente e Granadinas', 'San Vicente y las Granadinas'],
    'WS': ['Samoa', 'Samoa', 'Samoa'],
    'SM': ['San Marino', 'San Marino', 'San Marino'],
    'ST': ['Sao Tome and Principe', 'São Tomé e Príncipe', 'Santo Tomé y Príncipe'],
    'SA': ['Saudi Arabia', 'Arábia Saudita', 'Arabia Saudita'],
    'SN': ['Senegal', 'Senegal', 'Senegal'],
    'RS': ['Serbia', 'Sérvia', 'Serbia'],
    'SC': ['Seychelles', 'Seychelles', 'Seychelles'],
    'SL': ['Sierra Leone', 'Serra Leoa', 'Sierra Leona'],
    'SG': ['Singapore', 'Singapura', 'Singapur'],
    'SK': ['Slovakia', 'Eslováquia', 'Eslovaquia'],
    'SI': ['Slovenia', 'Eslovênia', 'Eslovenia'],
    'SB': ['Solomon Islands', 'Ilhas Salomão', 'Islas Salomón'],
    'SO': ['Somalia', 'Somália', 'Somalia'],
    'ZA': ['South Africa', 'África do Sul', 'Sudáfrica'],
    'KR': ['South Korea', 'Coreia do Sul', 'Corea del Sur'],
    'SS': ['South Sudan', 'Sudão do Sul', 'Sudán del Sur'],
    'ES': ['Spain', 'Espanha', 'España'],
    'LK': ['Sri Lanka', 'Sri Lanka', 'Sri Lanka'],
    'SD': ['Sudan', 'Sudão', 'Sudán'],
    'SR': ['Suriname', 'Suriname', 'Surinam'],
    'SZ': ['Swaziland', 'Suazilândia', 'Suazilandia'],
    'SE': ['Sweden', 'Suécia', 'Suecia'],
    'CH': ['Switzerland', 'Suíça', 'Suiza'],
    'SY': ['Syria', 'Síria', 'Siria'],
    'TW': ['Taiwan', 'Taiwan', 'Taiwán'],
    'TJ': ['Tajikistan', 'Tajiquistão', 'Tayikistán'],
    'TZ': ['Tanzania', 'Tanzânia', 'Tanzania'],
    'TH': ['Thailand', 'Tailândia', 'Tailandia'],
    'TL': ['Timor-Leste', 'Timor-Leste', 'Timor Oriental'],
    'TG': ['Togo', 'Togo', 'Togo'],
    'TO': ['Tonga', 'Tonga', 'Tonga'],
    'TT': ['Trinidad and Tobago', 'Trinidad e Tobago', 'Trinidad y Tobago'],
    'TN': ['Tunisia', 'Tunísia', 'Túnez'],
    'TR': ['Turkey', 'Turquia', 'Turquía'],
    'TM': ['Turkmenistan', 'Turcomenistão', 'Turkmenistán'],
    'TV': ['Tuvalu', 'Tuvalu', 'Tuvalu'],
    'UG': ['Uganda', 'Uganda', 'Uganda'],
    'UA': ['Ukraine', 'Ucrânia', 'Ucrania'],
    'AE': ['United Arab Emirates', 'Emirados Árabes Unidos', 'Emiratos Árabes Unidos'],
    'GB': ['United Kingdom', 'Reino Unido', 'Reino Unido'],
    'US': ['United States', 'Estados Unidos', 'Estados Unidos'],
    'UY': ['Uruguay', 'Uruguai', 'Uruguay'],
    'UZ': ['Uzbekistan', 'Uzbequistão', 'Uzbekistán'],
    'VU': ['Vanuatu', 'Vanuatu', 'Vanuatu'],
    'VA': ['Vatican City', 'Vaticano', 'Ciudad del Vaticano'],
    'VE': ['Venezuela', 'Venezuela', 'Venezuela'],
    'VN': ['Vietnam', 'Vietnã', 'Vietnam'],
    'YE': ['Yemen', 'Iêmen', 'Yemen'],
    'ZM': ['Zambia', 'Zâmbia', 'Zambia'],
    'ZW': ['Zimbabwe', 'Zimbábue', 'Zimbabue']
}


def remover_acentos(texto):
    """
    Remove acentos de um texto para facilitar comparações
    """
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


def buscar_iso_por_nome(nome_pais):
    """
    Busca o código ISO2 de um país pelo nome (em qualquer idioma)
    Suporta:
    - Match exato
    - Busca parcial (ex: "Braz" encontra "Brazil")
    - Fuzzy matching (tolera erros de digitação)
    
    Args:
        nome_pais: Nome do país em Português, Inglês ou Espanhol
    
    Returns:
        Código ISO2 ou None se não encontrado
    """
    if not nome_pais or not isinstance(nome_pais, str):
        return None
    
    nome_pais_limpo = nome_pais.strip()
    nome_pais_lower = nome_pais_limpo.lower()
    nome_pais_sem_acento = remover_acentos(nome_pais_lower)
    
    # 1. Tentativa: Match exato (case insensitive)
    for iso, nomes in PAISES_DATABASE.items():
        for nome in nomes:
            if nome.lower() == nome_pais_lower:
                return iso
    
    # 2. Tentativa: Match exato sem acentos
    for iso, nomes in PAISES_DATABASE.items():
        for nome in nomes:
            if remover_acentos(nome.lower()) == nome_pais_sem_acento:
                return iso
    
    # 3. Tentativa: Busca parcial - nome pesquisado está contido no nome do país
    for iso, nomes in PAISES_DATABASE.items():
        for nome in nomes:
            nome_lower = nome.lower()
            nome_sem_acento = remover_acentos(nome_lower)
            # Se o que foi digitado está contido no nome do país
            if nome_pais_lower in nome_lower or nome_pais_sem_acento in nome_sem_acento:
                return iso
    
    # 4. Tentativa: Busca parcial inversa - nome do país está contido no que foi digitado
    for iso, nomes in PAISES_DATABASE.items():
        for nome in nomes:
            nome_lower = nome.lower()
            nome_sem_acento = remover_acentos(nome_lower)
            # Se o nome do país está contido no que foi digitado
            if len(nome_lower) >= 3 and (nome_lower in nome_pais_lower or nome_sem_acento in nome_pais_sem_acento):
                return iso
    
    # 5. Tentativa: Fuzzy matching (similaridade > 80%)
    todos_nomes = []
    mapa_nome_iso = {}
    for iso, nomes in PAISES_DATABASE.items():
        for nome in nomes:
            nome_key = nome.lower()
            todos_nomes.append(nome_key)
            mapa_nome_iso[nome_key] = iso
    
    matches = get_close_matches(nome_pais_lower, todos_nomes, n=1, cutoff=0.8)
    if matches:
        return mapa_nome_iso[matches[0]]
    
    # Se não encontrou, retorna None
    return None


def buscar_nome_em_ingles(nome_pais):
    """
    Retorna o nome do país em inglês
    Usa a mesma lógica flexível de busca
    """
    # Primeiro busca o ISO usando a busca flexível
    iso = buscar_iso_por_nome(nome_pais)
    
    # Se encontrou o ISO, retorna o nome em inglês
    if iso and iso in PAISES_DATABASE:
        return PAISES_DATABASE[iso][0]
    
    # Se não encontrou, retorna o original
    return nome_pais


def processar_tabela_com_banco_paises(df_zonas):
    """
    Processa uma tabela de zonas, adicionando ISO e traduzindo para inglês
    
    Args:
        df_zonas: DataFrame com colunas 'country' e 'zone' (ou similar)
    
    Returns:
        DataFrame com colunas 'country' (em inglês), 'iso', 'zone'
    """
    import pandas as pd
    
    # Identifica a coluna de país (pode ter nomes diferentes)
    coluna_pais = None
    for col in df_zonas.columns:
        if 'countr' in col.lower() or 'pais' in col.lower() or 'país' in col.lower():
            coluna_pais = col
            break
    
    if not coluna_pais:
        raise ValueError("Coluna de país não encontrada. Certifique-se de que há uma coluna com 'country', 'pais' ou 'país' no nome.")
    
    # Identifica a coluna de zona
    coluna_zona = None
    for col in df_zonas.columns:
        if 'zone' in col.lower() or 'zona' in col.lower():
            coluna_zona = col
            break
    
    if not coluna_zona:
        raise ValueError("Coluna de zona não encontrada. Certifique-se de que há uma coluna com 'zone' ou 'zona' no nome.")
    
    # Cria novo DataFrame
    resultado = []
    
    for _, row in df_zonas.iterrows():
        nome_original = str(row[coluna_pais]).strip()
        zona = row[coluna_zona]
        
        # Busca ISO
        iso = buscar_iso_por_nome(nome_original)
        
        # Busca nome em inglês
        nome_ingles = buscar_nome_em_ingles(nome_original)
        
        resultado.append({
            'country': nome_ingles,
            'iso': iso if iso else 'XX',  # XX se não encontrar
            'Zona_Letra': zona
        })
    
    return pd.DataFrame(resultado)



