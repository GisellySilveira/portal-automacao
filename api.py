"""
API FastAPI para Portal de Automação de Frete
Backend que processa arquivos Excel e retorna arquivos ZIP
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import io
import zipfile
import tempfile
import os
from pathlib import Path
from typing import Optional, List
import json

from processador_excel import processar_arquivo_excel

app = FastAPI(
    title="Portal ShipSmart API",
    description="API para processamento de tabelas de frete",
    version="8.6"
)

# CORS - permite que frontend de qualquer origem acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates HTML
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    """Página inicial - renderiza o HTML"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health_check():
    """Health check - verifica se a API está funcionando"""
    return {
        "status": "ok",
        "version": "8.6",
        "message": "Portal ShipSmart API está funcionando!"
    }


@app.post("/api/processar-frete")
async def processar_frete(
    arquivo: UploadFile = File(...),
    transportadora: str = Form(...),
    nome_cliente: str = Form(...),
    adicionar_margem: bool = Form(True),
    usar_conversao_moeda: bool = Form(False),
    taxa_conversao: float = Form(1.0),
    incremento_peso: float = Form(0.1),
    converter_lb_kg: bool = Form(False),
    servicos_selecionados: Optional[str] = Form(None)  # JSON string com lista
):
    """
    Endpoint para processar tabelas de frete (exportação)
    
    Parâmetros:
    - arquivo: Arquivo Excel (.xlsx)
    - transportadora: FEDEX, UPS, DHL ou nome customizado
    - nome_cliente: Nome do cliente (obrigatório)
    - adicionar_margem: Gerar arquivos com margem (Lap, Special, etc.)
    - usar_conversao_moeda: Se deve aplicar conversão de moeda
    - taxa_conversao: Taxa de conversão (ex: 1.17)
    - incremento_peso: 0.1, 0.5 ou 1.0 kg
    - converter_lb_kg: Converter de libras para quilos
    - servicos_selecionados: JSON string com lista de serviços (ex: '["Priority", "Economy"]')
    
    Retorna:
    - Arquivo ZIP com todos os CSVs gerados
    """
    try:
        # Validações
        if not nome_cliente or nome_cliente.strip() == "":
            raise HTTPException(status_code=400, detail="Nome do cliente é obrigatório")
        
        # Lê o arquivo Excel em memória
        conteudo = await arquivo.read()
        arquivo_excel = io.BytesIO(conteudo)
        
        # Processa servicos_selecionados (se for FedEx)
        servicos_filtrar = None
        if servicos_selecionados:
            try:
                servicos_filtrar = json.loads(servicos_selecionados)
            except:
                servicos_filtrar = None
        
        # Processa o arquivo
        arquivos_gerados = processar_arquivo_excel(
            arquivo_excel,
            transportadora=transportadora.upper(),
            nome_cliente=nome_cliente.strip(),
            adicionar_margem=adicionar_margem,
            taxa_conversao=taxa_conversao if usar_conversao_moeda else 1.0,
            incremento_peso=incremento_peso,
            converter_lb_para_kg=converter_lb_kg,
            servicos_filtrar=servicos_filtrar,
            gerar_importacao=False
        )
        
        if not arquivos_gerados:
            raise HTTPException(status_code=400, detail="Nenhum arquivo foi gerado. Verifique o formato do Excel.")
        
        # Cria ZIP em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for nome_arquivo, conteudo_csv in arquivos_gerados.items():
                zip_file.writestr(nome_arquivo, conteudo_csv)
        
        zip_buffer.seek(0)
        
        # Salva temporariamente para enviar
        temp_dir = tempfile.gettempdir()
        temp_zip_path = os.path.join(temp_dir, f"resultados_{transportadora.lower()}_{nome_cliente}.zip")
        
        with open(temp_zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        # Retorna o arquivo
        return FileResponse(
            path=temp_zip_path,
            media_type='application/zip',
            filename=f"resultados_{transportadora.lower()}_{nome_cliente}.zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@app.post("/api/processar-importacao")
async def processar_importacao(
    arquivo: UploadFile = File(...),
    transportadora: str = Form(...),
    servico: str = Form(...),
    nome_cliente: str = Form(...),
    pais_destino: str = Form(...),
    iso_destino: str = Form(...),
    adicionar_margem: bool = Form(True),
    usar_conversao_moeda: bool = Form(False),
    taxa_conversao: float = Form(1.0),
    incremento_peso: float = Form(0.1),
    converter_lb_kg: bool = Form(False)
):
    """
    Endpoint para processar tabelas de importação (por zona)
    
    Parâmetros:
    - arquivo: Arquivo Excel (.xlsx)
    - transportadora: FEDEX, UPS, DHL ou nome customizado
    - servico: Nome do serviço (Priority, Economy, CP, etc.)
    - nome_cliente: Nome do cliente (obrigatório)
    - pais_destino: País de destino (ex: Brazil)
    - iso_destino: Código ISO (ex: BR)
    - adicionar_margem: Gerar arquivos com margem
    - usar_conversao_moeda: Se deve aplicar conversão de moeda
    - taxa_conversao: Taxa de conversão
    - incremento_peso: 0.1, 0.5 ou 1.0 kg
    - converter_lb_kg: Converter de libras para quilos
    
    Retorna:
    - Arquivo ZIP com todos os CSVs gerados (um por zona)
    """
    try:
        # Validações
        if not nome_cliente or nome_cliente.strip() == "":
            raise HTTPException(status_code=400, detail="Nome do cliente é obrigatório")
        
        if not pais_destino or pais_destino.strip() == "":
            raise HTTPException(status_code=400, detail="País de destino é obrigatório")
        
        if not iso_destino or iso_destino.strip() == "":
            raise HTTPException(status_code=400, detail="Código ISO é obrigatório")
        
        # Lê o arquivo Excel em memória
        conteudo = await arquivo.read()
        arquivo_excel = io.BytesIO(conteudo)
        
        # Processa o arquivo
        arquivos_gerados = processar_arquivo_excel(
            arquivo_excel,
            transportadora=transportadora.upper(),
            nome_cliente=nome_cliente.strip(),
            adicionar_margem=adicionar_margem,
            taxa_conversao=taxa_conversao if usar_conversao_moeda else 1.0,
            incremento_peso=incremento_peso,
            converter_lb_para_kg=converter_lb_kg,
            servicos_filtrar=[servico] if servico else None,
            gerar_importacao=True,
            pais_importacao=pais_destino.strip(),
            iso_importacao=iso_destino.strip()
        )
        
        if not arquivos_gerados:
            raise HTTPException(status_code=400, detail="Nenhum arquivo foi gerado. Verifique o formato do Excel.")
        
        # Filtra apenas arquivos de importação (contém "Zona")
        arquivos_importacao = {k: v for k, v in arquivos_gerados.items() if 'Zona' in k}
        
        if not arquivos_importacao:
            raise HTTPException(status_code=400, detail="Nenhum arquivo de importação foi gerado.")
        
        # Cria ZIP em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for nome_arquivo, conteudo_csv in arquivos_importacao.items():
                zip_file.writestr(nome_arquivo, conteudo_csv)
        
        zip_buffer.seek(0)
        
        # Salva temporariamente
        temp_dir = tempfile.gettempdir()
        temp_zip_path = os.path.join(temp_dir, f"importacao_{pais_destino}_{transportadora.lower()}.zip")
        
        with open(temp_zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        # Retorna o arquivo
        return FileResponse(
            path=temp_zip_path,
            media_type='application/zip',
            filename=f"importacao_{pais_destino}_{transportadora.lower()}.zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@app.get("/api/paises")
async def listar_paises():
    """Lista os países disponíveis para importação"""
    paises = {
        "Brazil": "BR",
        "Mexico": "MX",
        "United States": "US",
        "Portugal": "PT",
        "Chile": "CL",
        "Argentina": "AR",
        "Colombia": "CO",
        "Peru": "PE",
        "Spain": "ES",
        "Germany": "DE",
        "France": "FR",
        "Italy": "IT",
        "United Kingdom": "GB",
        "China": "CN",
        "Japan": "JP",
        "Canada": "CA"
    }
    return paises


@app.get("/api/transportadoras")
async def listar_transportadoras():
    """Lista as transportadoras disponíveis"""
    return {
        "predefinidas": ["FEDEX", "UPS", "DHL"],
        "personalizada": "OUTRAS"
    }


@app.get("/api/servicos/{transportadora}")
async def listar_servicos(transportadora: str):
    """Lista os serviços disponíveis por transportadora"""
    servicos_map = {
        "FEDEX": ["Priority", "Economy", "CP"],
        "UPS": ["Express", "Standard"],
        "DHL": ["dhl"],
        "OUTRAS": ["Todos"]
    }
    
    transportadora_upper = transportadora.upper()
    if transportadora_upper in servicos_map:
        return {"servicos": servicos_map[transportadora_upper]}
    else:
        return {"servicos": ["Todos"]}


if __name__ == "__main__":
    import uvicorn
    
    # Cria diretórios se não existirem
    Path("static").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Portal ShipSmart API - FastAPI")
    print("=" * 60)
    print()
    print("URL: http://localhost:8000")
    print("Documentacao: http://localhost:8000/docs")
    print("Redoc: http://localhost:8000/redoc")
    print()
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

