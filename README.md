# 🎓 Pathfinder AI — Intelligent Learning Platform

A full-stack AI-powered learning platform that generates personalized career roadmaps, quizzes, daily tasks, and coaching — powered by **Groq LLM**, **FastAPI**, and **n8n** automation.

---

## 🗂️ Project Structure

```
ai-learning-platform/
│
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings & env vars
│   ├── database.py                # SQLAlchemy engine & session
│   ├── models/
│   │   └── models.py              # DB models (User, LearningPath, Progress, etc.)
│   ├── routes/
│   │   ├── auth.py                # Register / Login / Me
│   │   ├── curriculum.py          # AI curriculum generation
│   │   ├── quiz.py                # AI quiz generation & submission
│   │   ├── chatbot.py             # AI tutor chatbot
│   │   ├── progress.py            # Progress tracking, streaks, badges
│   │   └── automation.py          # n8n webhook triggers
│   └── services/
│       ├── groq_service.py        # All Groq LLM calls
│       └── auth_service.py        # JWT auth helpers
│
├── frontend/
│   └── index.html                 # Complete SPA (all 6 pages, no framework)
│
├── n8n/
│   └── workflow.json              # n8n automation workflow (import directly)
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone <your-repo>
cd ai-learning-platform
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your keys
```

Your `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your-super-secret-jwt-key-change-this
DATABASE_URL=sqlite:///./learning_platform.db
N8N_WEBHOOK_URL=http://localhost:5678/webhook
GROQ_MODEL=llama3-70b-8192
```

Get your free Groq API key at: https://console.groq.com

### 3. Start the Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 4. Open the Frontend

```bash
cd frontend
python -m http.server 3000
# Visit: http://localhost:3000
```

> The frontend works in **demo mode** without the backend. With backend running, it uses real Groq AI generation.

### 5. Setup n8n (Optional)

```bash
npm install -g n8n
n8n start
# Visit http://localhost:5678
# Import n8n/workflow.json via Workflows → Import from file
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login, get JWT |
| GET | `/api/auth/me` | Current user |
| POST | `/api/curriculum/generate` | AI curriculum |
| GET | `/api/curriculum/my-paths` | User's paths |
| POST | `/api/quiz/generate` | AI quiz |
| POST | `/api/quiz/submit` | Submit answers |
| POST | `/api/chat/message` | Chatbot message |
| POST | `/api/progress/update` | Log progress |
| GET | `/api/progress/dashboard` | Dashboard data |
| GET | `/api/progress/feedback` | AI feedback |

---

## 🎨 Frontend Pages

| Page | Features |
|------|----------|
| **Auth** | Glassmorphism login/register, floating labels |
| **Home** | Hero section, stats, how-it-works |
| **Programs** | 6 featured program cards |
| **Career Paths** | 4 presets + custom path → AI curriculum |
| **Dashboard** | Streak, badges, tasks, progress, AI feedback |
| **Quiz** | AI MCQ quiz with scoring and review |
| **Chatbot** | Floating AI tutor (context-aware) |

---

## 🏆 Gamification

| Badge | Condition |
|-------|-----------|
| ⚡ Consistent | 3-day streak |
| 🏆 7-Day Streak | 7 consecutive days |
| 🌟 30-Day Streak | 30 consecutive days |
| 🎓 Graduate | 100% course completion |

---

## 🚀 Deployment

**Backend** (Railway/Render):
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Frontend** — update `API` constant in `index.html`:
```js
const API = 'https://your-backend.railway.app/api';
```
Then deploy `frontend/` as a static site on Vercel/Netlify.

**Production DB** — swap SQLite for PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS (single-file SPA) |
| Backend | FastAPI (Python 3.11+) |
| Database | SQLite / PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| AI/LLM | Groq API — llama3-70b-8192 |
| Automation | n8n (self-hosted) |
| Fonts | Syne + DM Sans |

---

## 📄 License

MIT — free to use, modify, and distribute.
