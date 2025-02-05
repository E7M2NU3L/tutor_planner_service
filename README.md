# Study Timeline Generator API

A Flask-based REST API that generates personalized study plans using Google's Gemini AI. The service includes progress tracking and caching capabilities.

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Redis Cloud account
- Neon PostgreSQL database
- Google Gemini API key

### Environment Setup
Create a `.env` file in the root directory with:

env
DATABASE_URL=your_neon_db_url
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_USERNAME=your_redis_username
REDIS_PASSWORD=your_redis_password
GEMINI_API_KEY=your_gemini_api_key

### Running the Application
```bash
docker-compose up --build
```

## 📚 API Documentation

### 1. Create Study Plan
Creates a personalized study plan based on user inputs.

**Endpoint:** `POST /api/v1/timeline/study-plan`

**Headers:**
```json
{
    "user-id": "user123",
    "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
    "timelimit": "Months",
    "education": "UnderGraduate",
    "age": 20,
    "studyHours": 6,
    "studytime": "Morning",
    "prior": "Intermediate",
    "examdate": "2024-06-15",
    "exam": "Software Engineering Finals",
    "method": "VideoLectures",
    "revision": "Weekly",
    "breaks": "POMODORO",
    "availablehoursinWeekend": "8"
}
```

**Success Response:**
```json
{
    "status": "SUCCESS",
    "plan_id": 123,
    "study_plan": {
        "timeline": [
            {
                "date": "2024-03-15",
                "day_of_week": "Monday",
                "topics": [
                    {
                        "subject": "Software Design",
                        "topic": "SOLID Principles",
                        "resources": [
                            "Video: SOLID Design Principles",
                            "Practice: Design Patterns Implementation"
                        ],
                        "duration_minutes": 120,
                        "difficulty_level": "Intermediate"
                    }
                ],
                "revision_topics": ["Basic OOP Concepts"],
                "practice_tests": ["SOLID Principles Quiz"],
                "break_schedule": {
                    "method": "POMODORO",
                    "breaks": [
                        {
                            "after_minutes": 25,
                            "break_duration_minutes": 5
                        }
                    ]
                }
            }
        ],
        "weekly_summary": {
            "total_study_hours": 42,
            "key_focus_areas": ["Design Patterns", "Architecture"],
            "recommended_improvements": ["More practice exercises"]
        },
        "exam_readiness_score": {
            "current_score": 75,
            "confidence_level": "Good",
            "areas_to_improve": ["System Design", "Design Patterns"]
        }
    }
}
```

### 2. Update Progress
Updates the completion status of study topics.

**Endpoint:** `POST /api/v1/timeline/progress/{plan_id}`

**Request Body:**
```json
{
    "completed_topics": [
        "SOLID Principles",
        "Basic OOP Concepts"
    ]
}
```

**Success Response:**
```json
{
    "status": "SUCCESS",
    "progress": 25.5  // Percentage completed
}
```

### 3. Get Study Plan
Retrieves a specific study plan.

**Endpoint:** `GET /api/v1/timeline/study-plan/{plan_id}`

**Success Response:**
```json
{
    "status": "SUCCESS",
    "study_plan": {
        // Same structure as create study plan response
    }
}
```

## 🔧 Available Enums

### Time Range Options
- Days
- Months
- Years
- Weeks
- Hours

### Education Levels
- School
- UnderGraduate (UG)
- PostGraduate (PG)
- PHD
- CompetitiveExam
- SelfStudy

### Study Time Preferences
- Morning
- Afternoon
- Evening
- Night

### Prior Knowledge Levels
- Beginner
- Intermediate
- Advanced

### Study Methods
- VideoLectures
- Reading
- PracticeTests
- FlashCards

### Revision Frequency
- Daily
- Weekly
- BeforeExam

### Break Preferences
- POMODORO
- FIFTY_TWO_SEVENTEEN
- NINETY_MINUTE_CYCLE
- SIXTY_TEN
- FLOWTIME
- TWO_DAY_RULE
- REVERSE_POMODORO

## 🔒 Error Handling

All endpoints return error responses in the following format:

```json
{
    "status": "FAILURE",
    "error": "Error message description"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## 🚀 Development

### Running Tests
```bash
python -m pytest tests/
```

### Local Development
1. Create a virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run: `python src/main.py`

## 📝 Notes
- The API uses Redis for caching study plans
- Study plans are stored in PostgreSQL for persistence
- All timestamps are in UTC
- Progress tracking is cumulative
