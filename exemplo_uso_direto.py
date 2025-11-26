"""
Exemplo de uso direto do processador de Excel (sem interface Streamlit)

Este script mostra como usar o processador diretamente para processar
arquivos Excel de diferentes transportadoras.
"""

from processador_excel import processar_arquivo_excel
import os

def processar_e_salvar(caminho_excel, transportadora, pasta_saida='./resultados'):
    """
    Processa um arquivo Excel e salva os resultados em arquivos CSV
    
    Args:
        caminho_excel: Caminho para o arquivo Excel
        transportadora: 'FEDEX', 'UPS' ou 'DHL'
        pasta_saida: Pasta onde os arquivos serão salvos
    """
    
    print(f"\n{'='*60}")
    print(f"Processando arquivo: {os.path.basename(caminho_excel)}")
    print(f"Transportadora: {transportadora}")
    print(f"{'='*60}\n")
    
    try:
        # Processa o arquivo Excel
        arquivos_gerados = processar_arquivo_excel(caminho_excel, transportadora=transportadora)
        
        if not arquivos_gerados:
            print("❌ Nenhum arquivo foi gerado.")
            return
        
        # Cria a pasta de saída se não existir
        pasta_transportadora = os.path.join(pasta_saida, transportadora)
        os.makedirs(pasta_transportadora, exist_ok=True)
        
        # Salva cada arquivo CSV
        print(f"\n📁 Salvando arquivos em: {pasta_transportadora}")
        for arquivo in arquivos_gerados:
            caminho_arquivo = os.path.join(pasta_transportadora, arquivo['nome'])
            with open(caminho_arquivo, 'w', encoding='cp1252') as f:
                f.write(arquivo['dados'])
            print(f"   ✅ {arquivo['nome']}")
        
        print(f"\n{'='*60}")
        print(f"✅ SUCESSO! {len(arquivos_gerados)} arquivos gerados.")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()


# --- EXEMPLOS DE USO ---

if __name__ == "__main__":
    
    # EXEMPLO 1: Processar arquivo FEDEX
    # Descomente e ajuste o caminho do arquivo
    """
    processar_e_salvar(
        caminho_excel="C:/Users/usuario/Downloads/FEDEX_PT.xlsx",
        transportadora='FEDEX',
        pasta_saida='./resultados'
    )
    """
    
    # EXEMPLO 2: Processar arquivo UPS
    # Descomente e ajuste o caminho do arquivo
    """
    processar_e_salvar(
        caminho_excel="C:/Users/usuario/Downloads/UPS_TABELA.xlsx",
        transportadora='UPS',
        pasta_saida='./resultados'
    )
    """
    
    # EXEMPLO 3: Processar arquivo DHL
    # Descomente e ajuste o caminho do arquivo
    """
    processar_e_salvar(
        caminho_excel="C:/Users/usuario/Downloads/DHL_TABELA.xlsx",
        transportadora='DHL',
        pasta_saida='./resultados'
    )
    """
    
    # EXEMPLO 4: Processar múltiplas transportadoras de uma vez
    """
    arquivos_para_processar = [
        {"caminho": "C:/Users/usuario/Downloads/FEDEX_PT.xlsx", "transportadora": "FEDEX"},
        {"caminho": "C:/Users/usuario/Downloads/UPS_TABELA.xlsx", "transportadora": "UPS"},
        {"caminho": "C:/Users/usuario/Downloads/DHL_TABELA.xlsx", "transportadora": "DHL"},
    ]
    
    for item in arquivos_para_processar:
        if os.path.exists(item["caminho"]):
            processar_e_salvar(
                caminho_excel=item["caminho"],
                transportadora=item["transportadora"],
                pasta_saida='./resultados'
            )
        else:
            print(f"⚠️  Arquivo não encontrado: {item['caminho']}")
    """
    
    print("\n" + "="*60)
    print("INSTRUÇÕES DE USO:")
    print("="*60)
    print("\n1. Descomente um dos exemplos acima")
    print("2. Ajuste o caminho do arquivo Excel")
    print("3. Execute o script: python exemplo_uso_direto.py")
    print("\nOu use a interface web: streamlit run app.py")
    print("="*60 + "\n")


