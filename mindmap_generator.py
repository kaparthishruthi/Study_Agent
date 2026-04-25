from agent import ask_ai

def generate_mindmap_data(topic):
    """
    Generates structured mind map data using AI.
    Returns a dict with central topic and branches.
    """
    prompt = f"""
Create a structured mind map for the topic: {topic}

Return ONLY a JSON object in this exact format (no markdown, no explanation):

{{
  "center": "{topic}",
  "branches": [
    {{
      "name": "Branch Name 1",
      "children": ["subtopic1", "subtopic2", "subtopic3"]
    }},
    {{
      "name": "Branch Name 2",
      "children": ["subtopic1", "subtopic2", "subtopic3"]
    }},
    {{
      "name": "Branch Name 3",
      "children": ["subtopic1", "subtopic2", "subtopic3"]
    }},
    {{
      "name": "Branch Name 4",
      "children": ["subtopic1", "subtopic2", "subtopic3"]
    }},
    {{
      "name": "Branch Name 5",
      "children": ["subtopic1", "subtopic2", "subtopic3"]
    }}
  ]
}}

Give 5 branches with 3 children each. Keep names concise (under 5 words).
"""
    response = ask_ai(prompt)
    return response
