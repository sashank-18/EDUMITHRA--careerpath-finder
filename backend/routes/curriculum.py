from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.models import User, LearningPath
from services.auth_service import get_current_user
from services.groq_service import generate_curriculum, get_resource_recommendations

router = APIRouter()


class CurriculumRequest(BaseModel):
    career_path: str
    skill_level: str = "beginner"    # beginner / intermediate / expert
    hours_per_day: float = 2.0


@router.post("/generate")
async def generate(req: CurriculumRequest, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    try:
        curriculum = generate_curriculum(req.career_path, req.skill_level, req.hours_per_day)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    # Persist to database
    path = LearningPath(
        user_id=current_user.id,
        career_path=req.career_path,
        skill_level=req.skill_level,
        hours_per_day=req.hours_per_day,
        curriculum=curriculum,
        weekly_plan=curriculum.get("weekly_plan", []),
        daily_tasks=curriculum.get("weekly_plan", [{}])[0].get("daily_tasks", []) if curriculum.get("weekly_plan") else [],
    )
    db.add(path)
    db.commit()
    db.refresh(path)

    return {"learning_path_id": path.id, "curriculum": curriculum}


@router.get("/my-paths")
def get_my_paths(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    paths = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).all()
    return [
        {
            "id": p.id,
            "career_path": p.career_path,
            "skill_level": p.skill_level,
            "hours_per_day": p.hours_per_day,
            "status": p.status,
            "created_at": p.created_at,
        }
        for p in paths
    ]


@router.get("/{path_id}")
def get_path(path_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id, LearningPath.user_id == current_user.id
    ).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return path


@router.get("/resources/{topic}")
async def get_resources(topic: str, career_path: str = "General",
                        current_user: User = Depends(get_current_user)):
    try:
        resources = get_resource_recommendations(topic, career_path)
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{path_id}")
def delete_path(path_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id, LearningPath.user_id == current_user.id
    ).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    db.delete(path)
    db.commit()
    return {"message": "Deleted successfully"}
