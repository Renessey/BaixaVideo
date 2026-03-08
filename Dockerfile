# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Instala o FFmpeg e dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Flask vai usar
EXPOSE 5000

# Comando para rodar o app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "index:app"]