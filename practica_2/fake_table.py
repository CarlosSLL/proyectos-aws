import pandas as pd
import numpy as np

# Simulación de Ingesta Operativa (OLTP)
np.random.seed(101)
n = 500

df_operativo = pd.DataFrame({
    'id_transaccion': range(1000, 1000 + n),
    'fecha_hora': pd.date_range(start='2026-01-01', periods=n, freq='h'),
    'cliente_nombre': np.random.choice(['Juan Pérez', 'María Gómez', 'Carlos Ruiz'], n),
    'cliente_ciudad': np.random.choice(['Puebla', 'CDMX', 'Guadalajara'], n),
    'producto_nombre': np.random.choice(['Laptop Dell', 'Mouse Logi', 'Monitor LG'], n),
    'categoria_prod': np.random.choice(['Cómputo', 'Accesorios', 'Pantallas'], n),
    'precio_unitario': np.random.choice([15000.0, 350.0, 4500.0], n),
    'cantidad': np.random.randint(1, 5, n),
    'canal_venta': np.random.choice(['Online', 'Tienda Física', 'App Móvil'], n),
    'porcentaje_descuento': np.random.choice([0.0, 0.05, 0.10, 0.15], n) # Atributo transaccional
})

# 1. Construcción de Dimensión Cliente (Dim_Cliente)
dim_cliente = df_operativo[[
    'cliente_nombre',
    'cliente_ciudad'
]].drop_duplicates().reset_index(drop=True)
dim_cliente['id_cliente_sk'] = dim_cliente.index + 1  # Surrogate Key

# 2. Construcción de Dimensión Producto (Dim_Producto)
dim_producto = df_operativo[[
    'producto_nombre', 'categoria_prod', 'precio_unitario'
]].drop_duplicates().reset_index(drop=True)
dim_producto['id_producto_sk'] = dim_producto.index + 1

# 3. Nueva Dimensión Adicional: Dimensión Canal (Dim_Canal)
dim_canal = df_operativo[['canal_venta']].drop_duplicates().reset_index(drop=True)
dim_canal['id_canal_sk'] = dim_canal.index + 1

# 4. Construcción de Dimensión Tiempo (Dim_Tiempo) ampliada
dim_tiempo = pd.DataFrame({
    'fecha_completa': df_operativo['fecha_hora'].dt.date.unique()
})
dim_tiempo['fecha_completa'] = pd.to_datetime(dim_tiempo['fecha_completa'])
dim_tiempo['id_tiempo_sk'] = (
    dim_tiempo['fecha_completa'].dt.strftime('%Y%m%d').astype(int)
)
dim_tiempo['anio'] = dim_tiempo['fecha_completa'].dt.year
dim_tiempo['mes'] = dim_tiempo['fecha_completa'].dt.month
dim_tiempo['nombre_mes'] = dim_tiempo['fecha_completa'].dt.strftime('%B')
dim_tiempo['dia'] = dim_tiempo['fecha_completa'].dt.day
dim_tiempo['trimestre'] = dim_tiempo['fecha_completa'].dt.quarter

# Atributos adicionales requeridos en Dim_Tiempo
dim_tiempo['numero_dia_semana'] = dim_tiempo['fecha_completa'].dt.dayofweek
dim_tiempo['dia_semana'] = dim_tiempo['fecha_completa'].dt.strftime('%A')
dim_tiempo['es_fin_semana'] = dim_tiempo['numero_dia_semana'].apply(lambda x: 1 if x >= 5 else 0)

# 5. Construcción de la Tabla de Hechos (Fact_Ventas) con Atributos Calculados
fact_ventas = (
    df_operativo.merge(dim_cliente, on=['cliente_nombre', 'cliente_ciudad'])
    .merge(dim_producto, on=['producto_nombre', 'categoria_prod', 'precio_unitario'])
    .merge(dim_canal, on='canal_venta')
)
fact_ventas['fecha_completa'] = pd.to_datetime(fact_ventas['fecha_hora'].dt.date)
fact_ventas = fact_ventas.merge(dim_tiempo, on='fecha_completa')

# Cálculos financieros en la Fact Table
fact_ventas['monto_bruto'] = fact_ventas['cantidad'] * fact_ventas['precio_unitario']
fact_ventas['monto_descuento'] = fact_ventas['monto_bruto'] * fact_ventas['porcentaje_descuento']
fact_ventas['monto_subtotal'] = fact_ventas['monto_bruto'] - fact_ventas['monto_descuento']

# Cálculo de IVA (16%)
TASA_IVA = 0.16
fact_ventas['monto_impuesto'] = (fact_ventas['monto_subtotal'] * TASA_IVA).round(2)
fact_ventas['monto_neto_total'] = (fact_ventas['monto_subtotal'] + fact_ventas['monto_impuesto']).round(2)

# Selección final de Fact Table
fact_table = fact_ventas[[
    'id_transaccion', 'id_cliente_sk', 'id_producto_sk', 'id_canal_sk',
    'id_tiempo_sk', 'cantidad', 'precio_unitario', 'porcentaje_descuento',
    'monto_bruto', 'monto_descuento', 'monto_subtotal', 'monto_impuesto', 'monto_neto_total'
]]

print("=== DIMENSIÓN TIEMPO (DIM_TIEMPO) ===")
print(dim_tiempo.head())

print("\n=== NUEVA DIMENSIÓN CANAL (DIM_CANAL) ===")
print(dim_canal)

print("\n=== TABLA DE HECHOS ENRIQUECIDA (FACT_VENTAS) ===")
print(fact_table.head())