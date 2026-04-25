from agent import ask_ai

def generate_notes(topic, difficulty):

    prompt = f"""
Generate structured study notes on the topic: {topic}

Difficulty level: {difficulty}

Format:

Title

Introduction

Key Concepts (bullet points)

Examples

Summary
"""

    return ask_ai(prompt)
