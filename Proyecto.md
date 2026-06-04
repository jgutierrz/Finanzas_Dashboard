# Finanzas Dashboard — Estado Actual del Proyecto

## 📌 Objetivo del Proyecto

Construir un dashboard personal modular conectado a Notion mediante API para administrar:

1. Finanzas personales
2. Inventario
3. Suscripciones (futuro)

El proyecto usa:

- Python
- Streamlit
- Pandas
- OpenPyXL
- API de Notion

---

# 🏗️ Arquitectura Actual

```text
Finanzas Dashboard/
│
├── app/
│   ├── app.py
│   └── pages/
│       ├── 01_Finanzas.py
│       ├── 02_Inventario.py   (pendiente)
│       └── 03_Suscripciones.py (futuro)
│
├── data/
│   └── processed/
│       ├── datos.csv
│       └── inventario.csv
│
├── domain/
│   ├── finanzas/
│   │   ├── extractor.py
│   │   └── metrics.py
│   │
│   └── inventory/
│       └── extractor.py
│
├── infrastructure/
│   ├── config.py
│   └── notion_client.py
│
├── scripts/
│   ├── update_data.py
│   └── update_inventory.py
│
├── services/
│   ├── finanzas_service.py
│   └── inventory_service.py
│
├── exporters/
│   └── excel_exporter.py
│
├── .env
│
└── requirements.txt

✅ Módulo Finanzas — Estado
✔️ Funciona actualmente
Conexión a Notion API
Extracción de movimientos
Resolución de categorías relacionadas
Dashboard Streamlit
KPIs
Alertas
Insights
Exportación Excel profesional

📊 Excel Exporter — Características implementadas
Hojas generadas
1. Movimientos
Todos los registros
AutoFiltro
Zoom 80%
Fecha formateada
Moneda S/
2. Resumen
Ingresos
Gastos
Balance
Score financiero
Promedio mensual
3. Pivot_Categorias
Gastos agrupados por mes/categoría
4. Resumen_Mensual

Incluye:

Ingresos
Gastos
Balance
% gastos
% ahorro
variación mensual
5. Top_Gastos
Top 50 gastos
✅ Mejoras ya implementadas
Ajuste automático de columnas
Bordes
Encabezados ejecutivos
Zoom 80%
Congelar fila superior
Formato moneda
Exclusión columna categoria_id
Arquitectura modular
⚠️ Pendiente/Revisión
Formato condicional Excel

Se intentó implementar:

balance negativo en rojo
ahorro negativo
gasto > 80%

Pero OpenPyXL no está aplicando correctamente las reglas.
Se decidió continuar y revisarlo después.