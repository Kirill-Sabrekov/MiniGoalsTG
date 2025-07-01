import hashlib
import hmac
import json
import time
from typing import Optional, Dict, Any
import jwt
from urllib.parse import parse_qs, urlparse

from .config import (
    BOT_TOKEN,
    JWT_ACCESS_SECRET,
    JWT_REFRESH_SECRET,
    ACCESS_TOKEN_EXPIRES_IN,
    REFRESH_TOKEN_EXPIRES_IN
)

def validate_init_data(init_data: str) -> Optional[Dict[str, Any]]:
    """
    Валидирует initData от Telegram Mini App
    """
    try:
        # Парсим initData
        parsed_data = parse_qs(init_data)
        
        # Проверяем наличие обязательных полей
        if 'hash' not in parsed_data:
            return None
            
        # Извлекаем hash
        received_hash = parsed_data['hash'][0]
        
        # Создаем строку для проверки (все поля кроме hash)
        check_string = []
        for key, value in parsed_data.items():
            if key != 'hash':
                check_string.append(f"{key}={value[0]}")
        
        # Сортируем по алфавиту
        check_string.sort()
        check_string = '\n'.join(check_string)
        
        # Создаем секретный ключ из bot token
        secret_key = hmac.new(
            "WebAppData".encode(),
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сравниваем hash
        if calculated_hash != received_hash:
            return None
            
        # Проверяем время (не старше 1 часа)
        if 'auth_date' in parsed_data:
            auth_date = int(parsed_data['auth_date'][0])
            if time.time() - auth_date > 3600:
                return None
        
        # Извлекаем данные пользователя
        user_data = {}
        if 'user' in parsed_data:
            user_data = json.loads(parsed_data['user'][0])
            
        return {
            'user': user_data,
            'auth_date': int(parsed_data.get('auth_date', [0])[0]),
            'query_id': parsed_data.get('query_id', [None])[0]
        }
        
    except Exception as e:
        print(f"Error validating init_data: {e}")
        return None

def create_access_token(user_data: Dict[str, Any]) -> str:
    """
    Создает access JWT токен
    """
    payload = {
        'user_id': user_data.get('id'),
        'username': user_data.get('username'),
        'first_name': user_data.get('first_name'),
        'last_name': user_data.get('last_name'),
        'exp': int(time.time()) + ACCESS_TOKEN_EXPIRES_IN,
        'type': 'access'
    }
    return jwt.encode(payload, JWT_ACCESS_SECRET, algorithm='HS256')

def create_refresh_token(user_data: Dict[str, Any]) -> str:
    """
    Создает refresh JWT токен
    """
    payload = {
        'user_id': user_data.get('id'),
        'username': user_data.get('username'),
        'first_name': user_data.get('first_name'),
        'last_name': user_data.get('last_name'),
        'exp': int(time.time()) + REFRESH_TOKEN_EXPIRES_IN,
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm='HS256')

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Проверяет access JWT токен
    """
    try:
        payload = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=['HS256'])
        if payload.get('type') != 'access':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Проверяет refresh JWT токен
    """
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def refresh_tokens(refresh_token: str) -> Optional[Dict[str, str]]:
    """
    Обновляет пару токенов используя refresh токен
    """
    payload = verify_refresh_token(refresh_token)
    if not payload:
        return None
        
    user_data = {
        'id': payload['user_id'],
        'username': payload.get('username'),
        'first_name': payload.get('first_name'),
        'last_name': payload.get('last_name')
    }
    
    return {
        'access_token': create_access_token(user_data),
        'refresh_token': create_refresh_token(user_data)
    } 