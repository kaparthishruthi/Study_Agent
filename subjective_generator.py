from agent import ask_ai

def generate_subjective_questions(topic: str, difficulty: str) -> str:
    prompt = f"""Create subjective questions on the topic: {topic}
Difficulty: {difficulty}

Generate EXACTLY in this format:

SHORT ANSWER QUESTIONS
======================
Q1: [question]
Model Answer: [2-3 sentence answer]

Q2: [question]
Model Answer: [2-3 sentence answer]

Q3: [question]
Model Answer: [2-3 sentence answer]

LONG ANSWER QUESTIONS
=====================
Q1: [question]
Model Answer: [detailed 5-8 sentence answer with examples]

Q2: [question]
Model Answer: [detailed 5-8 sentence answer with examples]

Generate 3 short answer and 2 long answer questions.
"""
    return ask_ai(prompt)
