"""
Script simples para rodar o servidor FastAPI
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Portal ShipSmart API - FastAPI")
    print("=" * 60)
    print()
    print("URL: http://localhost:8000")
    print("Documentacao: http://localhost:8000/docs")
    print()
    print("=" * 60)
    print()
    print("Iniciando servidor...")
    print("Quando aparecer 'Uvicorn running', acesse o navegador!")
    print()
    
    # Importa a app do api.py
    from api import app
    
    # Roda sem reload para evitar problemas
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


