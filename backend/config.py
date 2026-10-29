# config.py
# Configuration Settings

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# API Settings (key lives in .env, never commit it)
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/qwen-2.5-7b-instruct")

# Files
MENU_FILE = os.path.join(BASE_DIR, "Indian_restaurant_menu_Extract.xlsx")
ORDERS_FILE = os.path.join(BASE_DIR, "orders_log.json")

# Embedding Settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"

# GST rate applied on the receipt
GST_RATE = 0.18
