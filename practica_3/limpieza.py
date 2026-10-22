import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import KNNImputer, SimpleImputer

# Configuración del estilo gráfico
sns.set_theme(style="whitegrid")

# ---------------------------------------------------------
# Generación de dataset con ruido sintético
# ---------------------------------------------------------
data = {
    'edad': [25, 30, np.nan, 45, 22, 120, 35, 28, np.nan, 40],  # 120 es atípico/erróneo
    'ingreso_mensual': [15000, 22000, 18000, np.nan, 12000, 950000, 25000, 21000, 19000, np.nan],  # 950k outlier
    'scoring_credito': [650, 700, 680, 710, 590, 800, 670, 640, 620, 730],
}

df_dirty = pd.DataFrame(data)

print("Conjunto de datos original:")
print(df_dirty)

# ---------------------------------------------------------
# VISUALIZACIÓN 1: Antes del tratamiento de Outliers
# ---------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.boxplot(data=df_dirty[['edad', 'ingreso_mensual']], ax=axes[0], palette="Set2")
axes[0].set_title("Antes: Boxplot de Edad e Ingreso Mensual (Con Outliers)")
axes[0].set_yscale("log")  # Escala logarítmica para poder visualizar la diferencia de magnitudes

sns.histplot(df_dirty['ingreso_mensual'], ax=axes[1], kde=True, color='red')
axes[1].set_title("Antes: Distribución de Ingreso Mensual")

plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# 1. Tratamiento de Valores Atípicos por IQR sobre 'ingreso_mensual'
# ---------------------------------------------------------
Q1 = df_dirty['ingreso_mensual'].quantile(0.25)
Q3 = df_dirty['ingreso_mensual'].quantile(0.75)
IQR = Q3 - Q1

print("\nIQR:", IQR, "\nCuartil 1:", Q1, "\nCuartil 3 (Q3):", Q3)

limite_superior = Q3 + 1.5 * IQR
print(f"Límite Superior para Outliers en Ingreso: ${limite_superior:,.2f}")

# Reemplazar outliers extremos con NaN para tratarlos en la imputación
df_dirty.loc[df_dirty['ingreso_mensual'] > limite_superior, 'ingreso_mensual'] = np.nan
df_dirty.loc[df_dirty['edad'] > 100, 'edad'] = np.nan  # Corrección de valor erróneo (Edad 120)

print("\nDataset con Outliers reemplazados por NaN:")
print(df_dirty)

# ---------------------------------------------------------
# 2. Imputación Múltiple Avanzada con KNNImputer (k=2)
# ---------------------------------------------------------
imputer = KNNImputer(n_neighbors=2)
df_clean_array = imputer.fit_transform(df_dirty)
df_clean = pd.DataFrame(df_clean_array, columns=df_dirty.columns)

print("\n=== DATASET LIMPIO E IMPUTADO (KNN k=2) ===")
print(df_clean)

# ---------------------------------------------------------
# VISUALIZACIÓN 2: Después del tratamiento e imputación
# ---------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.boxplot(data=df_clean[['edad', 'ingreso_mensual']], ax=axes[0], palette="Set2")
axes[0].set_title("Después: Boxplot de Edad e Ingreso Mensual (Limpio)")

sns.histplot(df_clean['ingreso_mensual'], ax=axes[1], kde=True, color='green')
axes[1].set_title("Después: Distribución de Ingreso Mensual")

plt.tight_layout()
plt.show()