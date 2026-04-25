from agent import ask_ai

def generate_flashcards(topic):

    prompt = f"""
    Create flashcards for the topic:
    {topic}

    Format:
    Question:
    Answer:
    """

    return ask_ai(prompt)
