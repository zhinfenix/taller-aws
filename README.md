Solucion del taller :) ppunto 3

Arquitectura del Sistema
Backend: FastAPI corriendo sobre Uvicorn.
Base de Datos: Amazon RDS (PostgreSQL).
Almacenamiento de Archivos: Amazon S3.
Registro de Contenedores: Amazon ECR.
Computo Serverless: AWS Lambda con URL de funcion publica.
Endpoints Implementados
1. Cargar Imagen
Ruta: POST /upload
Descripcion: Recibe un archivo de imagen (unicamente formatos PNG o JPG), lo almacena en Amazon S3 bajo la estructura de carpetas del usuario y registra los metadatos en Amazon RDS.
2. Obtener Imagen
Ruta: GET /image
Descripcion: Consulta los metadatos en la base de datos de RDS y genera una URL prefirmada temporal para visualizar el archivo de forma segura desde Amazon S3.
Como ejecutar localmente con Docker
Construir la imagen: docker build -t fastapi-lambda-so .

Correr el contenedor: docker run -p 8000:8000 fastapi-lambda-so
