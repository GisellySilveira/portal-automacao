with open('processador_excel.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrige a linha 294 (índice 293)
if lines[293].strip().startswith('for nome_da_aba'):
    # Substitui por 8 espaços
    lines[293] = '        for nome_da_aba in abas_de_preco:\n'
    print('Linha 294 corrigida!')
else:
    print(f'Linha 294 não é o que esperávamos: {lines[293]}')

# Corrige a linha 295 (índice 294) se necessário
if lines[294].strip().startswith('# Verifica se a aba existe'):
    lines[294] = '            # Verifica se a aba existe no arquivo\n'
    print('Linha 295 corrigida!')

# Corrige a linha 296 (índice 295) se necessário
if lines[295].strip().startswith('if nome_da_aba not in'):
    lines[295] = '            if nome_da_aba not in xls.sheet_names:\n'
    print('Linha 296 corrigida!')

# Reescreve o arquivo
with open('processador_excel.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Arquivo reescrito!')


