from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import get_db
from models.models import User, QuizResult
from services.auth_service import get_current_user
from services.groq_service import generate_quiz

router = APIRouter()


class QuizRequest(BaseModel):
    career_path: str
    difficulty: str = "intermediate"
    num_questions: int = 10


class QuizSubmission(BaseModel):
    career_path: str
    answers: List[int]           # User's selected answer indices
    questions: List[dict]        # Full question data


@router.post("/generate")
async def get_quiz(req: QuizRequest, current_user: User = Depends(get_current_user)):
    try:
        quiz = generate_quiz(req.career_path, req.difficulty, req.num_questions)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.post("/submit")
async def submit_quiz(submission: QuizSubmission, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    score = 0
    results = []
    for i, question in enumerate(submission.questions):
        user_answer = submission.answers[i] if i < len(submission.answers) else -1
        correct = question.get("correct_answer", 0)
        is_correct = user_answer == correct
        if is_correct:
            score += 1
        results.append({
            "question": question.get("question"),
            "user_answer": user_answer,
            "correct_answer": correct,
            "is_correct": is_correct,
            "explanation": question.get("explanation", ""),
        })

    # Save result
    quiz_result = QuizResult(
        user_id=current_user.id,
        career_path=submission.career_path,
        score=score,
        total_questions=len(submission.questions),
        answers=submission.answers,
    )
    db.add(quiz_result)
    db.commit()

    return {
        "score": score,
        "total": len(submission.questions),
        "percentage": round((score / len(submission.questions)) * 100, 1) if submission.questions else 0,
        "results": results,
    }


@router.get("/history")
def quiz_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results = db.query(QuizResult).filter(QuizResult.user_id == current_user.id)\
        .order_by(QuizResult.taken_at.desc()).limit(10).all()
    return results
