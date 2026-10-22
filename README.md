# proyectos-aws

Prácticas de ingeniería de datos con Python y AWS (S3 y PostgreSQL). Esta guía te lleva paso a paso desde cero: entorno virtual, librerías, bucket S3, base de datos PostgreSQL en AWS y ejecución de cada práctica.

## Contenido

| Práctica | Qué hace | ¿Necesita AWS? |
|---|---|---|
| `practica_1` | Descarga un CSV y un JSON desde S3 y genera un perfilamiento con pandas | S3 |
| `practica_2` | Modelo dimensional (dimensiones + tabla de hechos) con datos simulados | No |
| `practica_3` | Limpieza de datos: outliers por IQR e imputación con KNN, con gráficas | No |
| `practica_4` | Dataset sintético con Faker y partición train/test estratificada | No |
| `practica_5` | Pipeline ETL: transforma datos, sube un Parquet a S3 y los guarda en PostgreSQL | S3 + PostgreSQL |

> Si solo quieres probar las prácticas 2, 3 y 4, basta con las secciones 1 y 2. AWS solo se necesita para las prácticas 1 y 5.

## 1. Requisitos previos

- **Python 3.11 o superior** (`python --version`). Descárgalo en [python.org](https://www.python.org/downloads/). En Windows marca *Add Python to PATH* al instalar.
- **Git** (`git --version`).
- Para las prácticas 1 y 5: una cuenta de **AWS Academy (Learner Lab)** o una cuenta de AWS con permisos sobre S3 y RDS/EC2.

## 2. Instalación del entorno

### 2.1 Clonar el repositorio

```bash
git clone https://github.com/CarlosSLL/proyectos-aws.git
cd proyectos-aws
```

### 2.2 Crear y activar el entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Si PowerShell bloquea el script (*"la ejecución de scripts está deshabilitada"*), ejecuta una vez:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Sabrás que está activo porque el prompt empieza con `(.venv)`. Cada vez que abras una terminal nueva debes activarlo de nuevo.

### 2.3 Instalar las librerías

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Comprueba que todo quedó bien:

```bash
python -c "import pandas, numpy, sklearn, matplotlib, seaborn, faker, boto3, yaml, pyarrow, sqlalchemy, psycopg; print('Todo OK')"
```

## 3. Ejecutar las prácticas que no usan AWS (2, 3 y 4)

Cada script debe ejecutarse **desde su propia carpeta**:

```bash
cd practica_2 && python fake_table.py && cd ..
cd practica_3 && python limpieza.py && cd ..
cd practica_4 && python ejercicio.py && cd ..
```

Notas:
- `practica_3` abre ventanas con gráficas (`plt.show()`). Cierra cada ventana para que el script continúe. En un servidor sin pantalla (por ejemplo una instancia EC2) ejecútalo así: `MPLBACKEND=Agg python limpieza.py`.
- `practica_4` usa `Faker('es_MX')`; los datos son siempre los mismos porque se fija la semilla.

---

## 4. Configuración de AWS (prácticas 1 y 5)

### 4.1 Obtener las credenciales (AWS Academy)

1. Entra a tu curso en AWS Academy → **Learner Lab** → **Start Lab** y espera a que el indicador se ponga en verde.
2. Haz clic en **AWS Details** → **AWS CLI: Show**.
3. Copia `aws_access_key_id`, `aws_secret_access_key` y `aws_session_token`.
4. La región normalmente es **`us-east-1`**.

> **Importante:** estas credenciales son temporales. Expiran cuando termina la sesión del laboratorio (error `ExpiredToken`). Cada vez que inicies el lab de nuevo debes copiar las credenciales nuevas en `config.yaml`.

### 4.2 Crear el archivo `config.yaml`

Los scripts leen un archivo llamado `config.yaml` **ubicado en la carpeta desde la que ejecutas el script**. Por seguridad este archivo está en el `.gitignore` y **nunca debe subirse a GitHub**.

Crea `practica_1/config.yaml` y `practica_5/config.yaml` con este contenido (puedes copiar el mismo archivo en ambas carpetas):

```yaml
aws:
  access_key_id: "ASIA................"
  secret_access_key: "pega_aqui_tu_secret"
  session_token: "pega_aqui_el_token_completo"
  region: "us-east-1"
  s3_bucket: "nombre-de-tu-bucket"                 # lo usa la práctica 5
  s3_key: "processed/etl_output.parquet"           # lo usa la práctica 5 (opcional)

s3:
  bucket_name: "nombre-de-tu-bucket"               # lo usa la práctica 1

postgres:                                          # lo usa la práctica 5
  host: "tu-endpoint.xxxxxx.us-east-1.rds.amazonaws.com"
  port: 5432
  database: "practicas"
  user: "postgres"
  password: "tu_password"
```

Reglas para que no falle:
- Respeta las claves exactamente como están escritas, incluyendo `session_token` (la práctica 1 la exige).
- Pon entre comillas los valores con caracteres especiales (`:`, `#`, `@`, etc.), sobre todo el password.
- `port` va sin comillas (es un número).
- Los espacios de indentación importan; no uses tabuladores.

---

## 5. Bucket S3

### 5.1 Crear el bucket

1. Consola de AWS → **S3** → **Create bucket**.
2. **Bucket name:** un nombre único global, en minúsculas (ej. `practicas-aws-tunombre-2026`).
3. **Region:** la misma que pusiste en `config.yaml` (`us-east-1`).
4. Deja activado **Block all public access**.
5. **Create bucket**.
6. Copia el nombre en `s3.bucket_name` y `aws.s3_bucket` de tu `config.yaml`.

### 5.2 Datos que necesita la práctica 1

La práctica 1 lee estos dos objetos del bucket:

```
raw/transacciones.csv
raw/logs_m2m.json
```

Si tienes los archivos originales del curso, súbelos con la ruta exacta anterior. Puedes hacerlo desde la consola (S3 → tu bucket → **Create folder** `raw` → **Upload**) o con Python, usando la misma conexión del proyecto:

```bash
cd practica_1
python -c "from conexion import conectar_s3; s3, b = conectar_s3(); s3.upload_file('transacciones.csv', b, 'raw/transacciones.csv'); s3.upload_file('logs_m2m.json', b, 'raw/logs_m2m.json'); print('Subidos')"
```

**¿No tienes los archivos?** Genera unos de ejemplo (datos ficticios) dentro de `practica_1`:

```python
import json
import numpy as np
import pandas as pd

np.random.seed(1)
n = 200
pd.DataFrame({
    "id_transaccion": range(1, n + 1),
    "monto": np.random.uniform(50, 5000, n).round(2),
    "cantidad": np.random.randint(1, 6, n),
    "canal": np.random.choice(["Online", "Tienda", "App"], n),
}).to_csv("transacciones.csv", index=False)

logs = [{"device": {"id": i, "tipo": "sensor"}, "lectura": {"temp": float(np.random.uniform(15, 35)), "humedad": float(np.random.uniform(30, 80))}} for i in range(100)]
with open("logs_m2m.json", "w", encoding="utf-8") as f:
    json.dump(logs, f)
```

Guárdalo como `generar_datos.py`, ejecútalo con `python generar_datos.py` y luego sube los archivos con el comando anterior.

### 5.3 Verificar la conexión a S3

Desde `practica_1`:

```bash
python -c "from conexion import conectar_s3; s3, b = conectar_s3(); s3.head_bucket(Bucket=b); print('Conexión a S3 OK:', b)"
```

---

## 6. PostgreSQL en AWS

Elige **una** de las dos opciones. La opción A (RDS) es la más sencilla porque AWS administra la instalación.

### Opción A: Amazon RDS (recomendada)

1. Consola de AWS → **RDS** → **Create database**.
2. **Standard create** → motor **PostgreSQL**.
3. **Templates:** *Free tier* (o *Dev/Test*).
4. **DB instance identifier:** `practicas-postgres`.
5. **Master username:** `postgres`. Define una **Master password** y guárdala.
6. **Instance configuration:** `db.t3.micro` (o `db.t4g.micro`). **Storage:** 20 GiB y desactiva el autoscaling de almacenamiento.
7. **Connectivity:** **Public access = Yes** y crea un **nuevo security group** (ej. `sg-practicas-postgres`).
8. Abre **Additional configuration** y en **Initial database name** escribe `practicas`.
9. **Create database**. Tarda entre 5 y 10 minutos en quedar *Available*.
10. Entra a la instancia y copia el **Endpoint** (algo como `practicas-postgres.abc123.us-east-1.rds.amazonaws.com`). Ese valor va en `postgres.host`.
11. **Abrir el puerto para tu IP:** pestaña **Connectivity & security** → clic en el security group → **Edit inbound rules** → **Add rule**: Type `PostgreSQL`, Port `5432`, Source `My IP` → **Save rules**.

> Las pantallas de AWS cambian de vez en cuando; los nombres de las opciones pueden variar ligeramente.

### Opción B: PostgreSQL instalado en una instancia EC2

1. Consola de AWS → **EC2** → **Launch instance**.
2. **AMI:** Amazon Linux 2023. **Tipo:** `t3.micro` (o `t2.micro`). Crea o elige un **key pair** y descarga el `.pem`.
3. **Security group**, reglas de entrada: `SSH` (22) desde *My IP* y `PostgreSQL` (5432) desde *My IP*.
4. Conéctate por SSH (el usuario es `ec2-user`):
   ```bash
   ssh -i tu-llave.pem ec2-user@IP_PUBLICA_DE_LA_INSTANCIA
   ```
5. Instala e inicializa PostgreSQL:
   ```bash
   sudo dnf install -y postgresql15 postgresql15-server
   sudo postgresql-setup --initdb
   sudo systemctl enable --now postgresql
   ```
   Si no encuentra el paquete, busca la versión disponible con `sudo dnf search postgresql`.
6. Crea la contraseña y la base de datos:
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   ALTER USER postgres WITH PASSWORD 'tu_password';
   CREATE DATABASE practicas;
   \q
   ```
7. Permite conexiones remotas:
   ```bash
   sudo nano /var/lib/pgsql/data/postgresql.conf
   ```
   Cambia `#listen_addresses = 'localhost'` por:
   ```
   listen_addresses = '*'
   ```
   Luego:
   ```bash
   sudo nano /var/lib/pgsql/data/pg_hba.conf
   ```
   Agrega al final (reemplaza `TU_IP_PUBLICA` por tu IP pública, la puedes ver en [checkip.amazonaws.com](https://checkip.amazonaws.com)):
   ```
   host    practicas    postgres    TU_IP_PUBLICA/32    scram-sha-256
   ```
8. Reinicia el servicio:
   ```bash
   sudo systemctl restart postgresql
   ```
9. En `config.yaml`, `postgres.host` es la **IPv4 pública** de la instancia. Esa IP cambia si detienes e inicias la instancia (a menos que uses una Elastic IP), y tu propia IP también puede cambiar: si de pronto deja de conectar, revisa ambas.

### Verificar la conexión a PostgreSQL

Desde `practica_5`, con el `config.yaml` ya creado:

```python
# probar_postgres.py
import yaml
from sqlalchemy import URL, create_engine, text

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))["postgres"]
url = URL.create(
    "postgresql+psycopg",
    username=cfg["user"], password=cfg["password"],
    host=cfg["host"], port=cfg["port"], database=cfg["database"],
)
engine = create_engine(url, connect_args={"connect_timeout": 10})
with engine.connect() as con:
    print(con.execute(text("SELECT version()")).scalar())
```

```bash
python probar_postgres.py
```

Si imprime la versión de PostgreSQL, la conexión funciona. Si se queda esperando y luego da *timeout*, es el security group o el acceso público (ver la sección 8).

---

## 7. Ejecutar las prácticas con AWS

### Práctica 1: perfilamiento desde S3

```bash
cd practica_1
python procesar_y_perfilar.py
```

Resultado esperado: dimensiones, tipos de datos y estadísticos de `transacciones.csv` y `logs_m2m.json`, y al final `=== PRÁCTICA FINALIZADA CORRECTAMENTE ===`.

### Práctica 5: pipeline ETL a S3 y PostgreSQL

```bash
cd practica_5
python pipeline.py
```

Resultado esperado: las fases de extracción, transformación y carga, con los mensajes *Archivo Parquet cargado correctamente en S3* y *Datos guardados correctamente en PostgreSQL*.

Para comprobar el resultado:
- **S3:** en la consola, bucket → carpeta `processed/` → `etl_output.parquet`.
- **PostgreSQL:**
  ```bash
  psql -h TU_HOST -U postgres -d practicas -c "SELECT * FROM clientes_transformados;"
  ```

> La práctica 5 inserta con `if_exists="append"`: **si la ejecutas dos veces, los 4 registros se duplican**. Para empezar limpio: `TRUNCATE clientes_transformados;`.

---

## 8. Solución de problemas

| Error | Causa probable | Solución |
|---|---|---|
| `FileNotFoundError` / `No such file or directory: 'config.yaml'` | Ejecutaste el script desde otra carpeta o falta el archivo | Entra a la carpeta de la práctica (`cd practica_1`) y verifica que `config.yaml` esté ahí |
| `KeyError: 'session_token'` (u otra clave) | Falta una clave en `config.yaml` | Compara con la plantilla de la sección 4.2 |
| `ExpiredToken` / "Las credenciales de AWS Academy han expirado" | La sesión del lab terminó | Reinicia el Learner Lab y copia las credenciales nuevas |
| `InvalidClientTokenId` / `SignatureDoesNotMatch` | Credenciales mal copiadas (faltó el token o sobran espacios) | Vuelve a copiar las tres credenciales completas |
| `NoSuchKey` | El archivo no está en `raw/` del bucket | Revisa el nombre y la ruta exactos (sección 5.2) |
| `NoSuchBucket` / `AccessDenied` | Nombre de bucket incorrecto, región distinta o sin permisos | Revisa `bucket_name` y `region` |
| `ModuleNotFoundError: No module named 'yaml'` | El paquete se instala como `pyyaml` | `pip install pyyaml` (o `pip install -r requirements.txt`) |
| `ImportError: cannot import name 'URL' from 'sqlalchemy'` | SQLAlchemy 1.x instalado | `pip install "sqlalchemy>=2.0"` |
| `ModuleNotFoundError: No module named 'psycopg'` | Falta el driver | `pip install "psycopg[binary]"`. Este proyecto usa **psycopg 3**, no `psycopg2` |
| `ImportError: ... pyarrow` | Falta el motor Parquet | `pip install pyarrow` |
| `connection timed out` hacia PostgreSQL | Security group sin tu IP, instancia sin acceso público o tu IP cambió | Revisa la regla de entrada 5432 con *My IP* y que *Public access* sea *Yes* |
| `password authentication failed` | Usuario o contraseña incorrectos | Revisa `postgres.user` / `postgres.password`; en RDS puedes cambiarla con **Modify** |
| `database "practicas" does not exist` | No se creó la base | En RDS usa `postgres` como `database`, o créala: `CREATE DATABASE practicas;` |
| `running scripts is disabled on this system` (PowerShell) | Política de ejecución | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| La práctica 3 no muestra gráficas | Entorno sin pantalla | `MPLBACKEND=Agg python limpieza.py` |
| `pip` instala en el Python global | El entorno virtual no está activo | Activa `.venv` (el prompt debe mostrar `(.venv)`) |

---

## 9. Seguridad y costos

- **Nunca subas `config.yaml` ni credenciales a GitHub.** El `.gitignore` ya excluye `**/config.yaml`. Si alguna vez publicas credenciales por error, desactívalas de inmediato y genera nuevas.
- Evita abrir el puerto 5432 a `0.0.0.0/0`; usa siempre *My IP*.
- Al terminar, **elimina o detén** la instancia RDS/EC2 y vacía/elimina el bucket para no generar costos o consumir el presupuesto del laboratorio.
- Recomendado en el `.gitignore` para no versionar archivos generados:
  ```
  __pycache__/
  *.pyc
  .venv/
  ```
