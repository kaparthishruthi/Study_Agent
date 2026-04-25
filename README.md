# 🧠 Study AI Agent

An AI-powered study companion built with **Streamlit** and **Groq**, designed to help students learn smarter — with notes generation, quizzes, mind maps, flashcards, study planning, and progress tracking.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Notes Generator** | Generate structured study notes on any topic |
| 📂 **Notes Uploader** | Upload `.txt`, `.md`, or `.pdf` files and get AI summaries + Q&A |
| 🧪 **Quiz Generator** | Auto-generate MCQ quizzes with difficulty levels and a live timer |
| 📅 **Study Planner** | Create hour-by-hour study schedules up to your exam date |
| 🗺️ **Mind Map Generator** | Visualize topics as interactive mind maps |
| 🃏 **Flashcard Generator** | Generate Q&A flashcards for quick revision |
| 📊 **Progress Tracker** | Track activity, quiz scores, and performance over time |
| 🔐 **User Auth** | Register and login with secure password hashing (SHA-256) |

---

## 🗂️ Project Structure

```
study_ai_agent_v2/
├── app.py                   # Main Streamlit app (UI & routing)
├── agent.py                 # Groq LLM wrapper (ask_ai)
├── auth.py                  # User registration & login
├── database.py              # SQLite DB init & connection
├── notes_generator.py       # Notes generation logic
├── notes_uploader.py        # File upload, summarize, Q&A from notes
├── quiz_generator.py        # MCQ quiz generation
├── flashcard_generator.py   # Flashcard generation
├── mindmap_generator.py     # Mind map data generation (JSON)
├── study_planner.py         # Hourly study plan generation
├── subjective_generator.py  # Subjective question generation
├── progress_tracker.py      # Progress & score persistence
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (API key)
└── study_agent.db           # SQLite database (auto-created)
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/study_ai_agent_v2.git
cd study_ai_agent_v2
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Your API Key

Create or edit the `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> Get a free API key at [console.groq.com](https://console.groq.com)

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **LLM Backend:** [Groq](https://groq.com/) (`llama-3.1-8b-instant`, `llama-3.3-70b-versatile`)
- **Database:** SQLite (via Python's built-in `sqlite3`)
- **PDF Parsing:** `pypdf`
- **Config:** `python-dotenv`

---

## 🗄️ Database Schema

The app automatically initializes a local SQLite database (`study_agent.db`) with the following tables:

| Table | Purpose |
|---|---|
| `users` | Stores registered users and hashed passwords |
| `progress` | Tracks topics studied per user |
| `scores` | Stores quiz results with percentages and difficulty |
| `saved_quizzes` | Full quiz history including questions and time taken |
| `saved_plans` | Saved study plans with subjects, exam date, and hours |

---

## 📋 Requirements

```
streamlit
groq
python-dotenv
pypdf        # for PDF file upload support
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🔒 Authentication

- Passwords are hashed using **SHA-256** before being stored.
- Each user gets their own isolated data (progress, scores, plans, quizzes).

---

## 📌 Notes

- The database file (`study_agent.db`) is created automatically on first run.
- Do **not** commit your `.env` file to version control. Add it to `.gitignore`:
  ```
  .env
  study_agent.db
  __pycache__/
  ```
- The app supports `.txt`, `.md`, and `.pdf` file uploads for the Notes Uploader feature.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is open-source. Feel free to use and modify it for personal or educational purposes.
