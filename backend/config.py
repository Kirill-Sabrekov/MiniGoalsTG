import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# JWT Secrets (в продакшене используйте безопасные секреты)
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET", "your_access_secret_key_here_change_in_production")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "your_refresh_secret_key_here_change_in_production")

# Token expiration times
ACCESS_TOKEN_EXPIRES_IN = 300  # 5 минут
REFRESH_TOKEN_EXPIRES_IN = 604800  # 7 дней

# CORS settings
ALLOWED_ORIGINS = [
    "https://fa3777315fb68c.lhr.life",  # Замените на ваш домен
] 