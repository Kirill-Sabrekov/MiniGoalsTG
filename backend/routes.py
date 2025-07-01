from fastapi import APIRouter, Depends, Request, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from .db import get_db
from .schemas import GoalCreate, GoalUpdate, GoalResponse
from .crud import create_goal, get_goal, get_goals, update_goal, delete_goal
from .models import User
from .logger import logger
from .telegram_auth import (
    validate_init_data, 
    create_access_token, 
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    refresh_tokens
)
from typing import Optional

router = APIRouter()

# JWT dependency для получения текущего пользователя
def get_current_user(
    access_token: Optional[str] = Cookie(None),
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token and not refresh_token:
        raise HTTPException(status_code=401, detail="No tokens provided")
    
    # Сначала пробуем access token
    if access_token:
        payload = verify_access_token(access_token)
        if payload:
            return payload['user_id']
    
    # Если access token не работает, пробуем refresh token
    if refresh_token:
        new_tokens = refresh_tokens(refresh_token)
        if new_tokens:
            # Здесь нужно будет обновить cookies в response
            # Пока что просто возвращаем user_id
            payload = verify_access_token(new_tokens['access_token'])
            if payload:
                return payload['user_id']
    
    raise HTTPException(status_code=401, detail="Invalid or expired tokens")

@router.post("/auth/signin")
async def signin(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Аутентификация через Telegram Mini App initData
    """
    try:
        body = await request.json()
        init_data = body.get("initData")
        
        if not init_data:
            raise HTTPException(status_code=400, detail="initData is required")
        
        # Валидируем initData
        validated_data = validate_init_data(init_data)
        if not validated_data:
            raise HTTPException(status_code=400, detail="Invalid initData")
        
        user_data = validated_data.get('user', {})
        telegram_id = user_data.get('id')
        
        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID not found in initData")
        
        # Ищем или создаем пользователя
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Создан новый пользователь: telegram_id={telegram_id}")
        else:
            # Обновляем данные пользователя если они изменились
            user.username = user_data.get('username')
            user.first_name = user_data.get('first_name')
            user.last_name = user_data.get('last_name')
            db.commit()
            logger.info(f"Обновлены данные пользователя: telegram_id={telegram_id}")
        
        # Создаем токены
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        # Устанавливаем cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # Для HTTPS
            samesite="strict",
            max_age=300  # 5 минут
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # Для HTTPS
            samesite="strict",
            max_age=604800  # 7 дней
        )
        
        logger.info(f"Успешная аутентификация: telegram_id={telegram_id}")
        return {"success": True, "user_id": user.id}
        
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.post("/auth/refresh")
async def refresh_auth(
    response: Response,
    refresh_token: Optional[str] = Cookie(None)
):
    """
    Обновление токенов
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    new_tokens = refresh_tokens(refresh_token)
    if not new_tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Устанавливаем новые cookies
    response.set_cookie(
        key="access_token",
        value=new_tokens['access_token'],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=300
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_tokens['refresh_token'],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=604800
    )
    
    return {"success": True}

@router.post("/auth/logout")
async def logout(response: Response):
    """
    Выход из системы
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"success": True}

@router.get("/auth/me")
async def get_current_user_info(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Получение информации о текущем пользователе
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

# Обновленные роуты для целей с новой системой авторизации
@router.post("/goals/", response_model=GoalResponse)
def create_goal_route(
    goal: GoalCreate, 
    user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_goal = create_goal(db, user_id, goal)
    logger.info(f"Создана цель '{goal.title}' для user_id={user_id}")
    return db_goal

@router.get("/goals/{goal_id}", response_model=GoalResponse)
def read_goal_route(
    goal_id: int, 
    user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_goal = get_goal(db, user_id, goal_id)
    if db_goal is None:
        logger.warning(f"Цель не найдена: id={goal_id}, user_id={user_id}")
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_goal

@router.get("/goals/", response_model=list[GoalResponse])
def list_goals_route(
    user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    goals = get_goals(db, user_id)
    logger.info(f"Получен список целей для user_id={user_id}, всего: {len(goals)}")
    return goals

@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal_route(
    goal_id: int, 
    goal: GoalUpdate, 
    user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_goal = update_goal(db, user_id, goal_id, goal)
    if db_goal is None:
        logger.warning(f"Цель не найдена для обновления: id={goal_id}, user_id={user_id}")
        raise HTTPException(status_code=404, detail="Goal not found")
    logger.info(f"Обновлена цель id={goal_id} для user_id={user_id}")
    return db_goal

@router.delete("/goals/{goal_id}")
def delete_goal_route(
    goal_id: int, 
    user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    ok = delete_goal(db, user_id, goal_id)
    if not ok:
        logger.warning(f"Цель не найдена для удаления: id={goal_id}, user_id={user_id}")
        raise HTTPException(status_code=404, detail="Goal not found")
    logger.info(f"Удалена цель id={goal_id} для user_id={user_id}")
    return {"detail": "Goal deleted"} 