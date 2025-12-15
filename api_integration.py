"""
Módulo de integração com a API ShipSmart
Envia tabelas de frete processadas para o backend da empresa
"""
import requests
import io
from typing import Optional, Dict, Any


class APIShipSmart:
    """Cliente para integração com a API ShipSmart"""
    
    def __init__(self, base_url: str = "https://bck.shipsmart.com.br/api", token: str = None):
        """
        Inicializa o cliente da API
        
        Args:
            base_url: URL base da API
            token: Bearer token para autenticação
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "accept": "application/json",
            "lang": "pt"
        }
        
        if self.token:
            self.headers["authorization"] = f"Bearer {self.token}"
    
    def verificar_senha(self, password: str) -> Dict[str, Any]:
        """
        Verifica se a senha está correta
        
        Args:
            password: Senha para verificar
            
        Returns:
            Resposta da API
        """
        url = f"{self.base_url}/auth/verify-password"
        payload = {"password": password}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Erro ao verificar senha: {str(e)}"
            }
    
    def enviar_tabela(
        self, 
        arquivo_conteudo: bytes, 
        nome_arquivo: str,
        tipo: int = 4,
        descricao: str = ""
    ) -> Dict[str, Any]:
        """
        Envia uma tabela de frete para a API
        
        Args:
            arquivo_conteudo: Conteúdo do arquivo em bytes
            nome_arquivo: Nome do arquivo
            tipo: Tipo da configuração (padrão: 4)
            descricao: Descrição da tabela
            
        Returns:
            Resposta da API
        """
        if not self.token:
            return {
                "status": "error",
                "message": "Token de autenticação não configurado"
            }
        
        url = f"{self.base_url}/configuracoes"
        
        # Prepara o arquivo
        files = {
            'arquivo': (nome_arquivo, arquivo_conteudo, 'text/csv')
        }
        
        # Prepara os dados do formulário
        data = {
            'tipo': str(tipo),
            'descricao': descricao
        }
        
        try:
            response = requests.post(
                url, 
                files=files, 
                data=data, 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Erro ao enviar tabela: {str(e)}",
                "details": str(e)
            }
    
    def enviar_multiplas_tabelas(
        self,
        arquivos: list,
        tipo: int = 4,
        descricao_base: str = ""
    ) -> list:
        """
        Envia múltiplas tabelas para a API
        
        Args:
            arquivos: Lista de dicionários com 'nome' e 'dados'
            tipo: Tipo da configuração
            descricao_base: Descrição base (será complementada com nome do arquivo)
            
        Returns:
            Lista com resultados de cada envio
        """
        resultados = []
        
        for arquivo in arquivos:
            nome = arquivo.get('nome', 'arquivo.csv')
            dados = arquivo.get('dados', '')
            
            # Converte string para bytes se necessário
            if isinstance(dados, str):
                dados_bytes = dados.encode('utf-8')
            else:
                dados_bytes = dados
            
            descricao = f"{descricao_base} - {nome}" if descricao_base else nome
            
            resultado = self.enviar_tabela(
                arquivo_conteudo=dados_bytes,
                nome_arquivo=nome,
                tipo=tipo,
                descricao=descricao
            )
            
            resultados.append({
                'arquivo': nome,
                'status': resultado.get('status'),
                'message': resultado.get('message'),
                'sucesso': resultado.get('status') == 'success'
            })
        
        return resultados
    
    def listar_tabelas(self, page: int = 1) -> Dict[str, Any]:
        """
        Lista as tabelas de frete cadastradas
        
        Args:
            page: Número da página
            
        Returns:
            Resposta da API com lista de tabelas
        """
        url = f"{self.base_url}/tabelas_fretes?page={page}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Erro ao listar tabelas: {str(e)}"
            }

