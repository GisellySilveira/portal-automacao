"""
Script de teste para a integração com a API ShipSmart
Execute este script para testar a conexão e envio de arquivos
"""

from api_integration import APIShipSmart
import json

def testar_integracao():
    """Testa a integração com a API ShipSmart"""
    
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO COM API SHIPSMART")
    print("=" * 60)
    print()
    
    # Carrega configurações
    try:
        with open("config_api.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo config_api.json não encontrado!")
        print("   Execute o Streamlit e configure as credenciais primeiro.")
        return
    
    token = config.get("token", "")
    password = config.get("password", "")
    api_url = config.get("api_url", "https://bck.shipsmart.com.br/api")
    
    if not token or not password:
        print("❌ Token ou senha não configurados!")
        print("   Configure no Streamlit primeiro.")
        return
    
    # Inicializa API
    print(f"🔗 Conectando à API: {api_url}")
    api = APIShipSmart(base_url=api_url, token=token)
    print("✅ Cliente API inicializado")
    print()
    
    # Teste 1: Verificar senha
    print("📝 TESTE 1: Verificação de Senha")
    print("-" * 60)
    resultado_senha = api.verificar_senha(password)
    print(f"Status: {resultado_senha.get('status')}")
    print(f"Mensagem: {resultado_senha.get('message')}")
    
    if resultado_senha.get('status') == 'success':
        print("✅ Autenticação bem-sucedida!")
    else:
        print("❌ Falha na autenticação")
        return
    print()
    
    # Teste 2: Listar tabelas (opcional)
    print("📝 TESTE 2: Listar Tabelas Cadastradas")
    print("-" * 60)
    resultado_lista = api.listar_tabelas(page=1)
    
    if resultado_lista.get('status') == 'success':
        data = resultado_lista.get('data', {})
        total = data.get('total', 0)
        print(f"✅ Total de tabelas cadastradas: {total}")
        
        if 'data' in data and len(data['data']) > 0:
            print(f"📊 Primeiras tabelas:")
            for idx, tabela in enumerate(data['data'][:3], 1):
                print(f"   {idx}. {tabela.get('descricao', 'Sem descrição')}")
    else:
        print(f"⚠️ Não foi possível listar tabelas: {resultado_lista.get('message')}")
    print()
    
    # Teste 3: Envio de arquivo de teste (comentado por segurança)
    print("📝 TESTE 3: Envio de Arquivo de Teste")
    print("-" * 60)
    print("⚠️ Teste de envio desabilitado para evitar envios acidentais")
    print("   Para testar o envio, use o botão no Streamlit após processar uma tabela.")
    print()
    
    print("=" * 60)
    print("TESTES CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    testar_integracao()

