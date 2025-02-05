from flask import Flask, jsonify, request
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import google.generativeai as genai
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

# Enums for input validation
class TimeRangeEnum(Enum):
    Days = 'Days'
    Months = 'Months'
    Years = 'Years'
    Weeks = 'Weeks'
    Hours = 'Hours'

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Invalid EducationLevel: {value}")

class EducationLevel(Enum):
    School = 'School'
    UnderGraduate = "UG"
    PostGraduate = "PG"
    PHD = "PHD"
    CompetitiveExam = 'CompetitiveExam'
    SelfStudy = 'SelfStudy'

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Invalid EducationLevel: {value}")


class StudyTime(Enum):
    Morning = "Morning"
    Afternoon = "Afternoon"
    Evening = "Evening"
    Night = "Night"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Invalid EducationLevel: {value}")

class PriorKnowledge(Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Invalid EducationLevel: {value}")

class PreferredStudyMethods(Enum):
    VideoLectures = "VideoLectures"
    Reading = "Reading"
    PracticeTests = "PracticeTests"
    FlashCards = "FlashCards"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Invalid EducationLevel: {value}")

class RevisionFrequency(Enum):
    Daily = "Daily"
    Weekly = "Weekly"
    BeforeExam = "BeforeExam"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Invalid EducationLevel: {value}")

class BreakPreferences(Enum):
    Pomodoro = "POMODORO"
    FiftyTwoSeventeen = "FIFTY_TWO_SEVENTEEN"
    NinetyMinuteCycle = "NINETY_MINUTE_CYCLE"
    SixtyTen = "SIXTY_TEN"
    Flowtime = "FLOWTIME"
    TwoDayRule = "TWO_DAY_RULE"
    ReversePomodoro = "REVERSE_POMODORO"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Invalid EducationLevel: {value}")

# Dataclass for user input
@dataclass
class PromptTypes:
    timelimit: TimeRangeEnum
    education: EducationLevel
    age: int
    studyHours: int
    studytime: StudyTime
    prior: PriorKnowledge
    examdate: str
    exam: str
    method: PreferredStudyMethods
    revision: RevisionFrequency
    breaks: BreakPreferences
    availablehoursinWeekend: str

# Dataclasses for output schema
@dataclass
class Break:
    after_minutes: int
    break_duration_minutes: int

@dataclass
class BreakSchedule:
    method: str
    breaks: List[Break]

@dataclass
class Topic:
    subject: str
    topic: str
    resources: List[str]
    duration_minutes: int
    difficulty_level: str

@dataclass
class StudyDay:
    date: str
    day_of_week: str
    topics: List[Topic]
    revision_topics: List[str]
    practice_tests: List[str]
    break_schedule: BreakSchedule
    notes: Optional[str] = None

@dataclass
class WeeklySummary:
    total_study_hours: int
    key_focus_areas: List[str]
    recommended_improvements: List[str]

@dataclass
class ExamReadiness:
    current_score: int
    confidence_level: str
    areas_to_improve: List[str]

@dataclass
class StudyPlan:
    timeline: List[StudyDay]
    weekly_summary: WeeklySummary
    exam_readiness_score: ExamReadiness

# Gemini API Wrapper
class GeminiConnection:
    _instance: Optional['GeminiConnection'] = None

    def __new__(cls, api_key: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(api_key)
        return cls._instance

    def _initialize(self, api_key: str) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")  # Use the right model version

    @lru_cache(maxsize=100)
    def get_model(self):
        return self.model

# Generate prompt for AI
class PromptGenerator:
    def __init__(self, prompt_data: PromptTypes):
        self.prompt_data = prompt_data

    def generate_prompt(self) -> str:
        return f"""
        Generate a structured study plan for a student with the following details:

        ## Personalization:
        - **Time Limit:** {self.prompt_data.timelimit.value}
        - **Education Level:** {self.prompt_data.education.value}
        - **Age:** {self.prompt_data.age}
        - **Preferred Study Hours per Day:** {self.prompt_data.studyHours}
        - **Preferred Study Time:** {self.prompt_data.studytime.value}

        ## Study Goals & Subjects:
        - **Prior Knowledge Level:** {self.prompt_data.prior.value}
        - **Exam Name:** {self.prompt_data.exam}
        - **Exam Date:** {self.prompt_data.examdate}

        ## Study Preferences:
        - **Preferred Study Method:** {self.prompt_data.method.value}
        - **Revision Frequency:** {self.prompt_data.revision.value}
        - **Break Preference:** {self.prompt_data.breaks.value}

        ## External Constraints:
        - **Available Hours on Weekends:** {self.prompt_data.availablehoursinWeekend}

        ### Instructions:
        1. The plan should be **structured and realistic**.
        2. Adjust difficulty and pacing based on prior knowledge.
        3. Include **study topics, practice tests, and revision schedules**.
        4. Suggest **break times and effective study techniques**.
        5. Ensure **flexibility** to accommodate external constraints.
        Provide the study plan in a **structured JSON format** following this schema:
        ```json
        {{
            "timeline": [{{"date": "YYYY-MM-DD", "day_of_week": "Monday", "topics": [...], "revision_topics": [...], "practice_tests": [...], "break_schedule": {{"method": "...", "breaks": [...]}} }}],
            "weekly_summary": {{"total_study_hours": 0, "key_focus_areas": [...], "recommended_improvements": [...] }},
            "exam_readiness_score": {{"current_score": 0, "confidence_level": "...", "areas_to_improve": [...] }}
        }}
        ```
        """

# Flask app
app = Flask(__name__)

# Health check endpoint
@app.route('/')
def health_checker():
    return jsonify({'message': 'App is running properly'})

# Study Plan Generator
@app.route("/api/v1/timeline", methods=['POST'])
def get_study_plan():
    # Parse request JSON
    data = request.json
    print(data)

    prompt_data = PromptTypes(
        timelimit=TimeRangeEnum.from_value(data['timelimit']),
        education = EducationLevel.from_value(data['education']),
        age=int(data['age']),
        studyHours=int(data['studyHours']),
        studytime=StudyTime.from_value(data['studytime']),
        prior=PriorKnowledge.from_value(data['prior']),
        examdate=data['examdate'],
        exam=data['exam'],
        method=PreferredStudyMethods.from_value(data['method']),
        revision=RevisionFrequency.from_value(data['revision']),
        breaks=BreakPreferences.from_value(data['breaks']),
        availablehoursinWeekend=data['availablehoursinWeekend']
    )
    print(prompt_data)

    # Generate prompt
    prompt_generator = PromptGenerator(prompt_data)
    prompt = prompt_generator.generate_prompt()
    print("Prompt generated")
    print(prompt)

    # Call Gemini API
    gemini = GeminiConnection(api_key=os.getenv('GOOGLE_GEMINI_KEY'))  # Replace with your API key
    model = gemini.get_model()
    response = model.generate_content(prompt)
    print(response.text)

    # Convert AI response to JSON
    study_plan = response.text  # Gemini usually returns text, ensure JSON parsing if needed

    return jsonify({'study_plan': study_plan}), 200

# Run server
if __name__ == '__main__':
    app.run(debug=True)