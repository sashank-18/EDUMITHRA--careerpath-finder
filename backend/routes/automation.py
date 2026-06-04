from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import requests

from models.models import User
from services.auth_service import get_current_user
from config import settings

router = APIRouter()


def _trigger_webhook(event: str, payload: dict):
    """Fire-and-forget n8n webhook trigger."""
    try:
        requests.post(
            f"{settings.N8N_WEBHOOK_URL}/{event}",
            json=payload,
            timeout=5
        )
    except Exception:
        pass  # Non-critical; log in production


class ReminderRequest(BaseModel):
    email: str
    user_name: str
    task: str
    career_path: str


@router.post("/daily-reminder")
def send_daily_reminder(req: ReminderRequest, background_tasks: BackgroundTasks,
                        current_user: User = Depends(get_current_user)):
    background_tasks.add_task(_trigger_webhook, "daily-reminder", {
        "email": req.email,
        "user_name": req.user_name,
        "task": req.task,
        "career_path": req.career_path,
    })
    return {"message": "Daily reminder queued"}


@router.post("/weekly-summary")
def send_weekly_summary(background_tasks: BackgroundTasks,
                        current_user: User = Depends(get_current_user)):
    background_tasks.add_task(_trigger_webhook, "weekly-summary", {
        "email": current_user.email,
        "user_name": current_user.name,
        "user_id": current_user.id,
    })
    return {"message": "Weekly summary queued"}


@router.post("/missed-task-alert")
def missed_task_alert(background_tasks: BackgroundTasks,
                      current_user: User = Depends(get_current_user)):
    background_tasks.add_task(_trigger_webhook, "missed-task", {
        "email": current_user.email,
        "user_name": current_user.name,
    })
    return {"message": "Missed task alert queued"}
