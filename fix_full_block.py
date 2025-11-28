with open('processador_excel.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar o início e fim do bloco for
start_idx = None
for i, line in enumerate(lines):
    if 'for nome_da_aba in abas_de_preco:' in line:
        start_idx = i
        print(f'Encontrado "for nome_da_aba" na linha {i+1}')
        break

if start_idx is None:
    print('Não encontrei o for!')
    exit(1)

# O for deve ter 8 espaços (dentro do try que tem 4)
# Todo o conteúdo do for deve ter pelo menos 12 espaços

# Vamos verificar e corrigir as linhas dentro do for
# O for vai até encontrarmos um except ou outra coisa no mesmo nível ou menor

fixes = []
i = start_idx + 1
while i < len(lines):
    line = lines[i]
    if line.strip() == '':
        i += 1
        continue
    
    # Se encontramos algo com 0-7 espaços (ou seja, fora do for), paramos
    indent = len(line) - len(line.lstrip())
    if indent < 8 and line.strip():
        print(f'Fim do bloco for na linha {i+1} (indent={indent})')
        break
    
    # Se a linha tem 8-11 espaços mas não é uma linha em branco, está errado
    if 8 <= indent < 12 and line.strip():
        # Adiciona 4 espaços para ficar em 12
        spaces_to_add = 12 - indent
        lines[i] = (' ' * spaces_to_add) + line
        fixes.append(f'Linha {i+1}: {indent} -> {12} espaços')
    
    i += 1

print(f'\\nCorreções aplicadas: {len(fixes)}')
for fix in fixes[:20]:  # Mostra só as primeiras 20
    print(f'  - {fix}')
if len(fixes) > 20:
    print(f'  ... e mais {len(fixes) - 20} correções')

# Reescreve o arquivo
with open('processador_excel.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\\nArquivo reescrito!')

