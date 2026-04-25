from agent import ask_ai

def generate_quiz(topic, difficulty):

    prompt = f"""
    Create 5 multiple choice quiz questions on {topic}.

    Difficulty: {difficulty}

    Format EXACTLY like this:

    Q1: Question

    A) option
    B) option
    C) option
    D) option

    Answer: Correct Option

    Explanation: Short explanation of why the answer is correct.

    """

    return ask_ai(prompt)
