import os 
from dotenv import load_dotenv 
load_dotenv() 
NOTION_TOKEN = os.getenv("NOTION_TOKEN") 
FINANZAS_DB_ID = os.getenv("FINANZAS_DB_ID") 
CATEGORIAS_DB_ID = os.getenv("CATEGORIAS_DB_ID") 
INVENTARIO_DB_ID = os.getenv("INVENTARIO_DB_ID") 
PERSONAL_DB_ID = os.getenv("PERSONAL_DB_ID")