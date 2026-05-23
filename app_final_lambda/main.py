import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import boto3
import psycopg2

app = FastAPI(title="Taller AWS - Sistemas Operativos 2026")

BUCKET_NAME = "user-1033183981-ueia-so"

DB_HOST = "db-taller-so.cpqkskiworsi.us-east-2.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "juanjose2518"

s3_client = boto3.client('s3')

def init_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=5432
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registro_imagenes (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(100) NOT NULL,
                ruta_s3 VARCHAR(255) NOT NULL,
                fecha_creacion TIMESTAMP NOT NULL
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("¡Conexión a RDS exitosa y tabla verificada!")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/upload")
async def upload_image(usuario: str = Form(...), file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=415, 
            detail="Formato inválido. Únicamente se aceptan archivos PNG o JPG/JPEG."
        )
    
    file_extension = file.filename.split(".")[-1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_key = f"{usuario}/imagen_{timestamp}.{file_extension}"
    
    try:
        file_content = await file.read()
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type
        )
        
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        fecha_actual = datetime.now()
        
        cursor.execute(
            "INSERT INTO registro_imagenes (usuario, ruta_s3, fecha_creacion) VALUES (%s, %s, %s) RETURNING id;",
            (usuario, s3_key, fecha_actual)
        )
        generated_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Imagen procesada correctamente",
            "data": {
                "id": generated_id,
                "usuario": usuario,
                "ruta_s3": s3_key,
                "fecha_creacion": fecha_actual
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en el despliegue: {str(e)}")

@app.get("/image")
def get_image(usuario: str, nombre_imagen: str):
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        
        query_path = f"{usuario}/{nombre_imagen}"
        cursor.execute(
            "SELECT id, usuario, ruta_s3, fecha_creacion FROM registro_imagenes WHERE usuario = %s AND ruta_s3 = %s;",
            (usuario, query_path)
        )
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Error: El usuario o la imagen especificada no existen en los registros de la universidad."
            )
        
        url_prefirmada = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': result[2]},
            ExpiresIn=3600
        )
        
        return {
            "usuario": result[1],
            "ruta_s3": result[2],
            "fecha_almacenamiento_rds": result[3],
            "url_acceso_prefirmada": url_prefirmada
        }
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar en los servicios: {str(e)}")





