FROM python:3.14-slim

# No escribir archivos .pyc y mandar los logs directo a la consola del contenedor
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Las dependencias se copian primero para aprovechar la caché de Docker: esta capa
# solo se reconstruye si cambia requirements.txt, no en cada cambio de código
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# El contenedor no necesita root para levantar uvicorn
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# host 0.0.0.0 para que el puerto sea alcanzable desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
