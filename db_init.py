import sqlite3

DB_FILE = "quiz_app.db"

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')

    conn.commit()
    conn.close()

def populate():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Seed quizzes
    quizzes = [("Python Quiz",), ("Math Quiz",)]
    cursor.executemany("INSERT INTO quizzes (name) VALUES (?)", quizzes)

    # Seed quiz questions
    questions = [
        # Python Quiz
        (1, "What is the output of 2 + 2?", "4,5,6,3", "4"),
        (1, "Which data type is mutable?", "List,Tuple,String,Integer", "List"),
        (1, "What keyword is used to define a function in Python?", "def,func,function,define", "def"),
        # Math Quiz
        (2, "What is the square of 8?", "64,56,72,81", "64"),
        (2, "What is 15 divided by 3?", "5,4,6,3", "5"),
        (2, "Solve: 12 x 5.", "50,60,70,80", "60")
    ]
    cursor.executemany("INSERT INTO quiz_questions (quiz_id, question, options, answer) VALUES (?, ?, ?, ?)", questions)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
    populate()
    print("Database setup complete with seed data!")
