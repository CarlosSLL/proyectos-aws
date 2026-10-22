import io
import os
import boto3
import yaml
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import URL, create_engine, text
from botocore.exceptions import ClientError, BotoCoreError
from sqlalchemy.exc import SQLAlchemyError


def cargar_configuracion(ruta_config: str = "config.yaml") -> dict:
    """Lee y carga las configuraciones desde un archivo YAML."""
    if not os.path.exists(ruta_config):
        raise FileNotFoundError(f"El archivo de configuración '{ruta_config}' no fue encontrado.")
    
    with open(ruta_config, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def pipeline_etl_completo(config: dict):

    # Extracción de parámetros de configuración
    aws_cfg = config["aws"]
    pg_cfg = config["postgres"]

    # =================================================
    # 1. EXTRACT: EXTRAER DATOS
    # =================================================

    print("\n=== 1. FASE DE EXTRACCION ===")

    # Datos simulados de clientes
    raw_data = {
        "cliente": ["A", "B", "C", "D"],
        "edad": [20, 40, 60, 30],
        "monto_compras": [1200.0, 50000.0, 30000.0, 15000.0]
    }

    df = pd.DataFrame(raw_data)
    print(df)

    # =================================================
    # 2. TRANSFORM: TRANSFORMAR DATOS
    # =================================================

    print("\n=== 2. FASE DE TRANSFORMACION ===")

    # Clasificar clientes según su edad
    df["categoria_edad"] = pd.cut(
        df["edad"],
        bins=[0, 25, 50, 100],
        labels=["Joven", "Adulto", "Senior"]
    )

    # Normalizar las compras entre 0 y 1
    scaler = MinMaxScaler()
    df["monto_normalizado"] = scaler.fit_transform(
        df[["monto_compras"]]
    ).ravel()

    # Crear un indicador promocional
    df["score_promocional"] = df["monto_normalizado"] * 100

    print("\nDatos transformados:")
    print(df)

    # =================================================
    # 3. LOAD: SUBIR ARCHIVO A AWS S3
    # =================================================

    print("\n=== 3. CARGA A AWS S3 ===")

    # Crear cliente de S3 usando las credenciales cargadas de YAML
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_cfg["access_key_id"],
        aws_secret_access_key=aws_cfg["secret_access_key"],
        aws_session_token=aws_cfg.get("session_token"),
        region_name=aws_cfg["region"]
    )

    # Convertir los datos a formato Parquet en memoria
    buffer = io.BytesIO()
    df.to_parquet(
        buffer,
        index=False,
        engine="pyarrow"
    )
    buffer.seek(0)

    # Subir el archivo al bucket
    s3_client.put_object(
        Bucket=aws_cfg["s3_bucket"],
        Key=aws_cfg.get("s3_key", "processed/etl_output.parquet"),
        Body=buffer.getvalue(),
        ContentType="application/vnd.apache.parquet"
    )

    print("Archivo Parquet cargado correctamente en S3.")

    # =================================================
    # 4. LOAD: GUARDAR DATOS EN POSTGRESQL
    # =================================================

    print("\n=== 4. CARGA A POSTGRESQL ===")

    # Crear la URL de conexión desde la configuración
    db_url = URL.create(
        drivername="postgresql+psycopg",
        username=pg_cfg["user"],
        password=pg_cfg["password"],
        host=pg_cfg["host"],
        port=pg_cfg["port"],
        database=pg_cfg["database"]
    )

    engine = create_engine(
        db_url,
        pool_pre_ping=True
    )

    try:
        # Crear la tabla si no existe
        with engine.begin() as conexion:
            conexion.execute(text("""
                CREATE TABLE IF NOT EXISTS clientes_transformados (
                    cliente VARCHAR(50),
                    edad INTEGER,
                    monto_compras DOUBLE PRECISION,
                    categoria_edad VARCHAR(20),
                    monto_normalizado DOUBLE PRECISION,
                    score_promocional DOUBLE PRECISION
                )
            """))

        # Insertar los datos transformados
        df.to_sql(
            name="clientes_transformados",
            con=engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        print("Datos guardados correctamente en PostgreSQL.")

    finally:
        engine.dispose()

    print("\n=== PIPELINE ETL FINALIZADO ===")


if __name__ == "__main__":
    try:
        configuracion = cargar_configuracion("config.yaml")
        pipeline_etl_completo(configuracion)

    except (ClientError, BotoCoreError) as error:
        print("\nError al conectar o cargar datos en AWS S3:")
        print(error)

    except SQLAlchemyError as error:
        print("\nError al conectar o guardar datos en PostgreSQL:")
        print(error)

    except Exception as error:
        print("\nOcurrió un error inesperado:")
        print(error)