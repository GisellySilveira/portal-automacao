with open('processador_excel.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Linha 593: return deve ter 8 espaços (dentro do try)
if 'return todos_os_arquivos_finais' in lines[592]:
    lines[592] = '        return todos_os_arquivos_finais\n'
    print('Linha 593 corrigida: return agora tem 8 espaços')

# Reescreve o arquivo
with open('processador_excel.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Arquivo reescrito!')


