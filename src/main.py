from flask import Flask, jsonify, request
from dataclasses import dataclass
from enum import Enum
from google import genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel

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
    title : str
    description : str
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
    subject : str

# Dataclasses for output schema
class Task(BaseModel):
  task : str
  time : str
  description : str

class Assignment(BaseModel):
  assignment : str
  time : str
  assignmentType : str
  description : str

class Timetable(BaseModel):
  day: str
  topic : str
  tasks : list[Task]
  assignments : list[Assignment]

# Gemini API Wrapper
gemini_key = os.getenv('GOOGLE_GEMINI_KEY')
client = genai.Client(api_key=gemini_key)
print("Google Gemini has been configured")

# Generate prompt for AI
class PromptGenerator:
    def __init__(self, prompt_data: PromptTypes):
        self.prompt_data = prompt_data

    def generate_prompt(self) -> str:
        return f"""
        Generate a structured study plan for a student for the specified time range with proper schema,
        the study plan is for a {self.prompt_data.age} year old {self.prompt_data.education.value} student, who is training for {self.prompt_data.exam} which is to be completed within {self.prompt_data.examdate}, he has {self.prompt_data.prior.value} level of knowledge in the subject and the subject is {self.prompt_data.subject} and he is very fond of learning through {self.prompt_data.breaks.value} technique and he likes to revises about the {self.prompt_data.revision.value} and he has {self.prompt_data.studyHours} of studying hours daily and for the weekends he has about {self.prompt_data.availablehoursinWeekend} hours for studying in the weekend, he studies mostly in the {self.prompt_data.studytime.value} and his method of study is {self.prompt_data.method.value}
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

     # Convert JSON data to PromptTypes instance
    prompt_data = PromptTypes(
        title=data["title"],
        description=data["description"],
        timelimit=TimeRangeEnum.from_value(data["timelimit"]),
        education=EducationLevel.from_value(data["education"]),
        age=data["age"],
        studyHours=data["studyHours"],
        studytime=StudyTime.from_value(data["studytime"]),
        prior=PriorKnowledge.from_value(data["prior"]),
        examdate=data["examdate"],
        exam=data["exam"],
        method=PreferredStudyMethods.from_value(data["method"]),
        revision=RevisionFrequency.from_value(data["revision"]),
        breaks=BreakPreferences.from_value(data["breaks"]),
        availablehoursinWeekend=data["availablehoursinWeekend"],
        subject=data["subject"]
    )

    # Generate prompt
    prompt_generator = PromptGenerator(prompt_data)
    prompt = prompt_generator.generate_prompt()


    # model configuration
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[Timetable],
    }

    # Call Gemini API
    response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=config,
        )

    # my_time_table: list[Timetable] = response.parsed
    # print([timetable.__dict__ for timetable in my_time_table])

    return jsonify({'study_plan': response.text}), 200

# Run server
if __name__ == '__main__':
    app.run(debug=True)