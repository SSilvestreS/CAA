# Dockerfile para Cidades Autônomas com Agentes de IA v1.6
# MLOps e Escalabilidade

# Multi-stage build para otimização
FROM python:3.9-slim as base

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Define diretório de trabalho
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Stage de desenvolvimento
FROM base as development

# Instala dependências de desenvolvimento
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy

# Copia código fonte
COPY . .

# Muda para usuário não-root
USER appuser

# Expõe porta
EXPOSE 8000

# Comando de desenvolvimento
CMD ["python", "-m", "uvicorn", "src.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage de produção
FROM base as production

# Copia código fonte
COPY . .

# Muda para usuário não-root
USER appuser

# Expõe porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de produção
CMD ["python", "-m", "uvicorn", "src.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

