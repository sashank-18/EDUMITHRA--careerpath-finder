from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from typing import Optional

from database import get_db
from models.models import User, Progress, Badge, LearningPath
from services.auth_service import get_current_user
from services.groq_service import generate_weekly_feedback

router = APIRouter()


class ProgressUpdate(BaseModel):
    learning_path_id: int
    tasks_completed: int
    tasks_total: int
    notes: Optional[str] = None


@router.post("/update")
def update_progress(update: ProgressUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    completion_pct = (update.tasks_completed / update.tasks_total * 100) if update.tasks_total else 0

    # Compute streak
    yesterday = datetime.utcnow() - timedelta(days=1)
    last_progress = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.date >= yesterday
    ).first()
    streak = (last_progress.streak_days + 1) if last_progress else 1

    progress = Progress(
        user_id=current_user.id,
        learning_path_id=update.learning_path_id,
        tasks_completed=update.tasks_completed,
        tasks_total=update.tasks_total,
        completion_pct=completion_pct,
        streak_days=streak,
        notes=update.notes,
    )
    db.add(progress)
    db.commit()

    # Badge checks
    _check_and_award_badges(db, current_user.id, streak, completion_pct)

    return {
        "tasks_completed": update.tasks_completed,
        "tasks_total": update.tasks_total,
        "completion_pct": completion_pct,
        "streak_days": streak,
    }


def _check_and_award_badges(db: Session, user_id: int, streak: int, completion_pct: float):
    existing_badges = db.query(Badge).filter(Badge.user_id == user_id).all()
    existing_types = {b.badge_type: b for b in existing_badges}

    qualified = set()
    if streak >= 7:
        qualified.add("week_streak")
    if streak >= 30:
        qualified.add("month_streak")
    if streak >= 3:
        qualified.add("consistency")
        
    completed_courses = db.query(Progress.learning_path_id).filter(
        Progress.user_id == user_id, 
        Progress.completion_pct >= 100
    ).distinct().count()
    
    if completion_pct >= 100 or completed_courses > 0:
        qualified.add("course_completion")
        
    if completed_courses >= 2:
        qualified.add("ninja")
        
    active_paths = db.query(LearningPath).filter(LearningPath.user_id == user_id).count()
    if active_paths >= 3:
        qualified.add("multitasker")

    for bt in qualified:
        if bt not in existing_types:
            db.add(Badge(user_id=user_id, badge_type=bt))
            
    for bt, badge in existing_types.items():
        if bt not in qualified:
            db.delete(badge)
            
    db.commit()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Latest progress
    latest = db.query(Progress).filter(Progress.user_id == current_user.id)\
        .order_by(Progress.date.desc()).first()

    # All progress for chart
    all_progress = db.query(Progress).filter(Progress.user_id == current_user.id)\
        .order_by(Progress.date).limit(30).all()

    # Badges
    badges = db.query(Badge).filter(Badge.user_id == current_user.id).all()

    # Learning paths
    paths = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).all()

    return {
        "streak_days": latest.streak_days if latest else 0,
        "completion_pct": latest.completion_pct if latest else 0,
        "tasks_completed": latest.tasks_completed if latest else 0,
        "tasks_total": latest.tasks_total if latest else 0,
        "badges": [{"type": b.badge_type, "earned_at": b.earned_at} for b in badges],
        "progress_history": [
            {"date": str(p.date)[:10], "completion_pct": p.completion_pct, "streak": p.streak_days}
            for p in all_progress
        ],
        "active_paths": len(paths),
    }


@router.get("/notes")
def get_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notes = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.notes != None,
        Progress.notes != ""
    ).order_by(Progress.date.desc()).all()
    
    return [
        {"id": n.id, "date": str(n.date)[:10], "notes": n.notes, "tasks_completed": n.tasks_completed, "tasks_total": n.tasks_total}
        for n in notes
    ]


@router.get("/feedback")
async def get_feedback(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recent = db.query(Progress).filter(Progress.user_id == current_user.id)\
        .order_by(Progress.date.desc()).limit(7).all()

    progress_data = {
        "user_name": current_user.name,
        "week_completion": [p.completion_pct for p in recent],
        "current_streak": recent[0].streak_days if recent else 0,
        "tasks_this_week": sum(p.tasks_completed for p in recent),
    }

    try:
        feedback = generate_weekly_feedback(progress_data)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
