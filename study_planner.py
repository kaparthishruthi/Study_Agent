from groq import Groq
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_plan(subjects, exam_date, hours):

    subject_list = [s.strip() for s in subjects.split(",")]

    start_date = datetime.today().date()
    exam = exam_date

    total_days = (exam - start_date).days

    if total_days <= 0:
        return "Exam date must be in the future."

    dates = []
    for i in range(1, total_days):
        day = start_date + timedelta(days=i)
        dates.append(str(day))

    prompt = f"""
Create a **hourly study plan** for the student.

Subjects:
{subjects}

Study hours per day: {hours}

Study dates:
{dates}

Rules:
- Divide study time hour-by-hour
- Assign subjects evenly
- Mention topics for each hour
- Format clearly

Example format:

2026-03-07

Hour 1:
Data Structures - Arrays

Hour 2:
Operating Systems - Process Management

Hour 3:
Data Structures - Linked Lists
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content
