import hmac
import hashlib
import time
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session
from .models import User
from .db import get_db
from .logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LOGIN_TTL = 60

def check_telegram_login(data: dict) -> dict:
    auth_date = int(data.get("auth_date", 0))
    if abs(time.time() - auth_date) > LOGIN_TTL:
        raise HTTPException(status_code=403, detail="Login expired")
    auth_data = {k: v for k, v in data.items() if k != "hash"}
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(auth_data.items()))
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if hmac_hash != data.get("hash"):
        raise HTTPException(status_code=403, detail="Invalid Telegram LoginUrl signature")
    return data

async def auth_telegram(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    check_telegram_login(data)
    telegram_id = data["id"]
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Создан новый пользователь с telegram_id={telegram_id}")
    return {"user_id": user.id} 