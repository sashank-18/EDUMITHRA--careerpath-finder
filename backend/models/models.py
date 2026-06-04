from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    learning_paths = relationship("LearningPath", back_populates="user")
    progress_records = relationship("Progress", back_populates="user")
    badges = relationship("Badge", back_populates="user")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_path = Column(String(200), nullable=False)
    skill_level = Column(String(50))
    hours_per_day = Column(Float, default=2.0)
    curriculum = Column(JSON)           # Full AI-generated curriculum
    weekly_plan = Column(JSON)          # Weekly breakdown
    daily_tasks = Column(JSON)          # Daily task list
    resources = Column(JSON)            # YouTube links & resources
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="learning_paths")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"))
    date = Column(DateTime(timezone=True), server_default=func.now())
    tasks_completed = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)
    completion_pct = Column(Float, default=0.0)
    streak_days = Column(Integer, default=0)
    notes = Column(Text)

    user = relationship("User", back_populates="progress_records")


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_type = Column(String(100))   # "week_streak", "completion", "consistency"
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="badges")


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_path = Column(String(200))
    score = Column(Integer)
    total_questions = Column(Integer)
    answers = Column(JSON)
    taken_at = Column(DateTime(timezone=True), server_default=func.now())
