from agent import ask_ai

def extract_text_from_upload(uploaded_file) -> str:
    """Extract plain text from uploaded .txt or .pdf file."""
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    if name.endswith(".txt") or name.endswith(".md"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    elif name.endswith(".pdf"):
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(uploaded_file.read()))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        except Exception as e:
            return f"[PDF read error: {e}]"
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

def summarize_notes(text: str) -> str:
    prompt = f"""You are a study assistant. Summarize the following notes clearly and concisely.

Structure your summary as:
- Key Topics Covered
- Main Concepts (bullet points)
- Important Definitions
- Key Takeaways

Notes:
{text[:6000]}
"""
    return ask_ai(prompt)

def answer_question_from_notes(text: str, question: str) -> str:
    prompt = f"""You are a study assistant. Answer the following question based ONLY on the notes provided.
If the answer is not in the notes, say so clearly.

Notes:
{text[:6000]}

Question: {question}

Give a clear, detailed answer.
"""
    return ask_ai(prompt)
