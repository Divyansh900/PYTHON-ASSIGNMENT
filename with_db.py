import sqlite3

DB_FILE = "quiz_app.db"

def db_connect():
    return sqlite3.connect(DB_FILE)

# User Management
def register():
    email = input("Enter your email: ").strip().lower()
    password = input("Enter your password: ").strip()

    with db_connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            print("Registration successful!")
        except sqlite3.IntegrityError:
            print("Email already registered!")

def login():
    email = input("Enter your email: ").strip().lower()
    password = input("Enter your password: ").strip()

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            return user[0]  # Return user ID
        else:
            print("Invalid email or password.")
            return None

# Quiz Management
def quiz_option():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM quizzes")
        return cursor.fetchall()

def quiz(user_id):
    quizzes = quiz_option()

    print("\nAvailable Quizzes:")
    for idx, (quiz_id, name) in enumerate(quizzes, start=1):
        print(f"{idx}. {name}")

    choice = input("Choose a quiz by number: ").strip()
    try:
        quiz_id = quizzes[int(choice) - 1][0]
    except (IndexError, ValueError):
        print("Invalid choice.")
        return

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT question, options, answer FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()

        if not questions:
            print("No questions available for this quiz.")
            return

        score = 0
        for question, options, answer in questions:
            print(f"\n{question}")
            options = options.split(",")  # Assuming options stored as "A,B,C,D"
            for idx, opt in enumerate(options, start=1):
                print(f"{idx}. {opt}")

            user_answer = input("Your answer: ").strip()
            try:
                if options[int(user_answer) - 1] == answer:
                    score += 1
            except (IndexError, ValueError):
                print("Invalid answer.")
        print("\n\n")
        print(f"You scored {score}/{len(questions)}!")
        print("\n\n")
        cursor.execute("INSERT INTO user_scores (user_id, quiz_id, score) VALUES (?, ?, ?)", (user_id, quiz_id, score))
        conn.commit()

# Main Menu
def main():
    current_user_id = None
    while True:
        print("\n1. Register\n2. Login\n3. Take Quiz\n4. Exit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            register()
        elif choice == '2':
            current_user_id = login()
        elif choice == '3':
            if current_user_id:
                quiz(current_user_id)
            else:
                print("Please log in first!")
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
