from sqlalchemy.orm import Session
from .models import Goal
from .schemas import GoalCreate, GoalUpdate

def create_goal(db: Session, user_id: str, goal: GoalCreate):
    db_goal = Goal(**goal.dict(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goal(db: Session, user_id: str, goal_id: int):
    return db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()

def get_goals(db: Session, user_id: str):
    return db.query(Goal).filter(Goal.user_id == user_id).all()

def update_goal(db: Session, user_id: str, goal_id: int, goal: GoalUpdate):
    db_goal = get_goal(db, user_id, goal_id)
    if not db_goal:
        return None
    for key, value in goal.dict(exclude_unset=True).items():
        setattr(db_goal, key, value)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, user_id: str, goal_id: int):
    db_goal = get_goal(db, user_id, goal_id)
    if not db_goal:
        return False
    db.delete(db_goal)
    db.commit()
    return True 