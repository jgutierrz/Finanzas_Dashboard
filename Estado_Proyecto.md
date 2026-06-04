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