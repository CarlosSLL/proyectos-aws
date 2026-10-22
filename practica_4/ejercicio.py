from faker import Faker
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

fake = Faker('es_MX')
Faker.seed(42)
np.random.seed(42)

# 1. Generación programática de dataset con Faker (Campos agregados: fecha_nacimiento y telefono)
registros = []
for i in range(1000):
    registros.append({
        'id_cliente': i + 1,
        'nombre': fake.name(),
        'email': fake.email(),
        'telefono': fake.phone_number(),
        'fecha_nacimiento': fake.date_of_birth(minimum_age=18, maximum_age=75),
        'estado_civil': np.random.choice(
            ['Soltero', 'Casado', 'Divorciado'], p=[0.5, 0.4, 0.1]
        ),
        'ingreso_anual': round(np.random.uniform(100000, 1000000), 2),
        'churn': np.random.choice([0, 1], p=[0.8, 0.2])  # 20% tasa de abandono
    })

df_sintetico = pd.DataFrame(registros)
print(df_sintetico)

# 2. Selección de Datos Objetivo (Target) y Características (Features)
# Excluimos identificadores únicos e información personal no predictiva
X = df_sintetico.drop(columns=['id_cliente', 'nombre', 'email', 'telefono', 'fecha_nacimiento', 'churn'])
y = df_sintetico['churn']

# 3. Codificación Numérica de Variables Categóricas
# Usamos pd.get_dummies para convertir 'estado_civil' en variables One-Hot (numéricas)
X_encoded = pd.get_dummies(X, columns=['estado_civil'], drop_first=False, dtype=int)

# 4. Partición Estratificada (Train 80%, Test 20%)
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.20, random_state=42, stratify=y
)

# Impresión de resultados para verificación
print("--- Primeras filas de X_encoded ---")
print(X_encoded.head())

print("\n--- Dimensiones del dataset ---")
print(f"Dimensiones Train Set: {X_train.shape} | Proporción Churn: {y_train.mean():.2f}")
print(f"Dimensiones Test Set: {X_test.shape} | Proporción Churn: {y_test.mean():.2f}")