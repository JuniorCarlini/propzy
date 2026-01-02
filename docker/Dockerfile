FROM python:3.13-slim

# Defina variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Instale dependências do sistema necessárias para desenvolvimento
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Configure o diretório de trabalho
WORKDIR /app

# Instale o UV e configure o PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv* /usr/local/bin/

# Copie os arquivos de dependência
COPY pyproject.toml uv.lock ./

# Instale as dependências com UV (inclui extras de desenvolvimento)
RUN uv sync --frozen --extra dev

# Ative o virtual environment permanentemente
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

# Verifique se o Django foi instalado corretamente
RUN python -m django --version

# Exponha a porta para desenvolvimento
EXPOSE 8080

# Comando padrão para desenvolvimento (será sobrescrito pelo devcontainer)
CMD ["sleep", "infinity"]
