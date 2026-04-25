import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_agent.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS progress (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            topic    TEXT NOT NULL,
            date     TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            topic      TEXT NOT NULL,
            score      INTEGER,
            total      INTEGER,
            percentage REAL,
            difficulty TEXT,
            date       TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS saved_quizzes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            topic      TEXT NOT NULL,
            difficulty TEXT,
            questions  TEXT,
            score      INTEGER,
            total      INTEGER,
            percentage REAL,
            time_taken INTEGER,
            date       TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS saved_plans (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT NOT NULL,
            subjects  TEXT,
            exam_date TEXT,
            hours     INTEGER,
            plan      TEXT,
            date      TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

init_db()
