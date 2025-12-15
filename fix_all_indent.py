with open('processador_excel.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# A linha 294 (índice 293) é o "for", que deve ter 8 espaços (dentro do try)
# Todo o conteúdo dentro desse for (294-590 aproximadamente) deve ter pelo menos 12 espaços

# Vamos corrigir linha por linha
fixes = []

# Linha 300: print deve ter 12 espaços (dentro do for)
if '--- Processando a aba:' in lines[299]:
    old = lines[299]
    lines[299] = '            print(f"\\n--- Processando a aba: \'{nome_da_aba}\' ---")\n'
    fixes.append(f'300: {len(old) - len(old.lstrip())} -> 12 espaços')

print(f'Correções aplicadas: {len(fixes)}')
for fix in fixes:
    print(f'  - {fix}')

# Reescreve o arquivo
with open('processador_excel.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Arquivo reescrito!')


