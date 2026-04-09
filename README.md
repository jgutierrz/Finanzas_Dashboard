finanzas-dashboard/
│
├── data/                  # Datos locales (NO subir a GitHub)
│   ├── raw/               # Datos crudos desde Notion
│   └── processed/         # Datos limpios
│
├── src/                   # Código fuente
│   ├── __init__.py
│   │
│   ├── config.py         # Tokens, config general
│   │
│   ├── notion_api.py     # Conexión con Notion
│   ├── extractor.py      # Extracción de datos
│   ├── transform.py      # Limpieza y transformación
│   ├── analysis.py       # Lógica financiera
│   │
│   └── utils.py          # Funciones auxiliares
│
├── app/                  # Dashboard
│   └── app.py
│
├── scripts/              # Scripts ejecutables
│   └── run_pipeline.py
│
├── requirements.txt
├── .env                  # Tokens (NO subir)
├── .gitignore
└── README.md