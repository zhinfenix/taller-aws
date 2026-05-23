# 1. Usamos una imagen ligera de Python
FROM python:3.11-slim

# 2. TRUCO AWS LAMBDA: Copiamos el adaptador oficial para que Uvicorn corra serverless
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.0.0 /lambda-adapter /opt/extensions/lambda-adapter
# 3. Configuramos la carpeta de trabajo
WORKDIR /app

# 4. Copiamos los requerimientos y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto del código (nuestro main.py)
COPY . .

# 6. Exponemos el puerto 8000

EXPOSE 8000

# 7. Comando para encender FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
