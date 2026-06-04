import json
import re
import requests
from config import settings


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def _call_groq(messages: list, max_tokens: int = 4096, temperature: float = 0.7) -> str:
    """Core Groq API call."""
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict | list:
    """Safely extract JSON from LLM response."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from code fence
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Fallback: find first JSON object/array
    match = re.search(r"(\{[\s\S]+\}|\[[\s\S]+\])", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not extract JSON from response: {text[:300]}")


def generate_curriculum(career_path: str, skill_level: str, hours_per_day: float) -> dict:
    """Generate a complete AI-driven curriculum for a career path."""
    prompt = f"""
You are an expert curriculum designer. Generate a comprehensive, structured learning curriculum.

Career Path: {career_path}
Skill Level: {skill_level}
Available Study Time: {hours_per_day} hours/day

Return ONLY valid JSON (no markdown, no explanation) in this exact structure:
{{
  "career_path": "{career_path}",
  "overview": "2-3 sentence overview of this career path",
  "total_duration_weeks": <integer>,
  "required_skills": ["skill1", "skill2", ...],
  "difficulty": "{skill_level}",
  "phases": [
    {{
      "phase": 1,
      "title": "Phase title",
      "duration_weeks": <integer>,
      "topics": [
        {{
          "name": "Topic name",
          "subtopics": ["subtopic1", "subtopic2"],
          "estimated_hours": <integer>,
          "youtube_query": "specific YouTube search query for this topic",
          "resources": ["resource1", "resource2"]
        }}
      ],
      "mini_project": {{
        "title": "Mini project title",
        "description": "Project description",
        "skills_practiced": ["skill1", "skill2"]
      }}
    }}
  ],
  "weekly_plan": [
    {{
      "week": 1,
      "theme": "Week theme",
      "goals": ["goal1", "goal2"],
      "daily_tasks": [
        {{"day": "Monday", "task": "Task description", "duration_hours": <float>}},
        {{"day": "Tuesday", "task": "Task description", "duration_hours": <float>}},
        {{"day": "Wednesday", "task": "Task description", "duration_hours": <float>}},
        {{"day": "Thursday", "task": "Task description", "duration_hours": <float>}},
        {{"day": "Friday", "task": "Task description", "duration_hours": <float>}},
        {{"day": "Saturday", "task": "Task description", "duration_hours": <float>}},
        {{"day": "Sunday", "task": "Review & rest", "duration_hours": <float>}}
      ]
    }}
  ],
  "capstone_project": {{
    "title": "Final project title",
    "description": "Detailed project description",
    "technologies": ["tech1", "tech2"],
    "estimated_weeks": <integer>
  }},
  "career_outcomes": ["outcome1", "outcome2", "outcome3"]
}}

Generate at least 3 phases and 4 weeks of detailed weekly plan. Make content specific and actionable.
"""
    raw = _call_groq([{"role": "user", "content": prompt}], max_tokens=4096)
    return _extract_json(raw)


def generate_quiz(career_path: str, difficulty: str = "intermediate", num_questions: int = 10) -> dict:
    """Generate a quiz for a career path."""
    prompt = f"""
You are an expert technical interviewer. Create a quiz for the following:

Career Path: {career_path}
Difficulty: {difficulty}
Number of Questions: {num_questions}

Return ONLY valid JSON (no markdown, no explanation) in this exact structure:
{{
  "career_path": "{career_path}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Why this answer is correct",
      "topic": "Topic this question covers"
    }}
  ]
}}

correct_answer is the 0-based index of the correct option. Make questions specific, technical, and varied in topic coverage.
"""
    raw = _call_groq([{"role": "user", "content": prompt}], max_tokens=3000)
    return _extract_json(raw)


def chat_response(user_message: str, career_path: str, conversation_history: list) -> str:
    """Generate a chatbot response in the context of a learning path."""
    system_prompt = f"""You are an expert AI tutor and mentor for the {career_path} learning path. 
You help students understand concepts, debug problems, and stay motivated.
Be concise, practical, and encouraging. Format code with backticks when relevant.
Focus on explaining concepts clearly with real-world examples."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    return _call_groq(messages, max_tokens=1024, temperature=0.8)


def generate_weekly_feedback(progress_data: dict) -> str:
    """Generate personalized weekly feedback."""
    prompt = f"""
As an AI learning coach, provide personalized weekly feedback based on this progress data:
{json.dumps(progress_data, indent=2)}

Write 3-4 sentences of encouraging, specific, actionable feedback. 
Acknowledge achievements, identify areas to improve, and suggest adjustments.
Be warm, specific, and motivating.
"""
    return _call_groq([{"role": "user", "content": prompt}], max_tokens=500, temperature=0.9)


def get_resource_recommendations(topic: str, career_path: str) -> dict:
    """Get curated resource recommendations for a topic."""
    prompt = f"""
Recommend learning resources for:
Topic: {topic}
Career Path: {career_path}

Return ONLY valid JSON:
{{
  "youtube_searches": ["search query 1", "search query 2", "search query 3"],
  "free_resources": [
    {{"name": "Resource name", "url": "https://...", "type": "documentation/article/course"}}
  ],
  "practice_sites": ["site1", "site2"],
  "estimated_hours": <integer>
}}
"""
    raw = _call_groq([{"role": "user", "content": prompt}], max_tokens=1000)
    return _extract_json(raw)
