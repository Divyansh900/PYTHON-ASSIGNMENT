from colorama import Fore, Style

# Storage for user data and quiz results
users = {}
quizzes = {
    "Python": [
        {"question": "What is the output of 2 + 2?", "options": ["4", "5", "6", "3"], "answer": "4"},
        {"question": "Which data type is mutable?", "options": ["List", "Tuple", "String", "Integer"], "answer": "List"}
    ],
    "Math": [
        {"question": "What is the square of 8?", "options": ["64", "56", "72", "81"], "answer": "64"},
        {"question": "What is 15 divided by 3?", "options": ["5", "4", "6", "3"], "answer": "5"}
    ]
}

# Registration
def register_user():
    print(Fore.CYAN + "\n--- Register ---" + Style.RESET_ALL)
    email = input(Fore.YELLOW + "Enter your email: " + Style.RESET_ALL).strip().lower()
    if email in users:
        print(Fore.RED + "This email is already registered." + Style.RESET_ALL)
        return
    password = input(Fore.YELLOW + "Enter your password: " + Style.RESET_ALL)
    users[email] = {"password": password, "quizzes": {}}
    print(Fore.GREEN + "Registration successful!" + Style.RESET_ALL)

# Login
def login_user():
    print(Fore.CYAN + "\n--- Login ---" + Style.RESET_ALL)
    email = input(Fore.YELLOW + "Enter your email: " + Style.RESET_ALL).strip().lower()
    if email not in users:
        print(Fore.RED + "Email not found. Please register first." + Style.RESET_ALL)
        return None
    password = input(Fore.YELLOW + "Enter your password: " + Style.RESET_ALL)
    if users[email]["password"] == password:
        print(Fore.GREEN + "Login successful!" + Style.RESET_ALL)
        return email
    print(Fore.RED + "Incorrect password." + Style.RESET_ALL)
    return None

# Quiz
def take_quiz(email):
    print(Fore.CYAN + "\n--- Quiz ---" + Style.RESET_ALL)
    print("Available quizzes:")
    for idx, quiz_name in enumerate(quizzes.keys(), start=1):
        print(f"{idx}. {quiz_name}")
    choice = input(Fore.YELLOW + "Choose a quiz by number: " + Style.RESET_ALL)
    try:
        quiz_name = list(quizzes.keys())[int(choice) - 1]
    except (ValueError, IndexError):
        print(Fore.RED + "Invalid choice. Try again." + Style.RESET_ALL)
        return

    score = 0
    for idx, question in enumerate(quizzes[quiz_name], start=1):
        print(Fore.CYAN + f"\nQ{idx}: {question['question']}" + Style.RESET_ALL)
        for i, option in enumerate(question["options"], start=1):
            print(f"{i}. {option}")
        answer = input(Fore.YELLOW + "Your answer (1-4): " + Style.RESET_ALL)
        try:
            if question["options"][int(answer) - 1] == question["answer"]:
                score += 1
        except (ValueError, IndexError):
            print(Fore.RED + "Invalid option. Skipping." + Style.RESET_ALL)

    print(Fore.GREEN + f"\nYou scored {score}/{len(quizzes[quiz_name])} in {quiz_name}!" + Style.RESET_ALL)
    users[email]["quizzes"][quiz_name] = score

# View Results
def view_results(email):
    print(Fore.CYAN + "\n--- Your Quiz Results ---" + Style.RESET_ALL)
    if not users[email]["quizzes"]:
        print(Fore.YELLOW + "No quizzes attempted yet." + Style.RESET_ALL)
        return
    for quiz_name, score in users[email]["quizzes"].items():
        print(Fore.GREEN + f"{quiz_name}: {score}/{len(quizzes[quiz_name])}" + Style.RESET_ALL)

# Main Menu
def main():
    current_user = None
    while True:
        print(Fore.CYAN + "\n1. Register\n2. Login\n3. Take Quiz\n4. View Results\n5. Logout\n6. Exit" + Style.RESET_ALL)
        choice = input(Fore.YELLOW + "Select an option: " + Style.RESET_ALL)
        if choice == '1':
            register_user()
        elif choice == '2':
            current_user = login_user()
        elif choice == '3':
            if current_user:
                take_quiz(current_user)
            else:
                print(Fore.RED + "You need to log in first!" + Style.RESET_ALL)
        elif choice == '4':
            if current_user:
                view_results(current_user)
            else:
                print(Fore.RED + "You need to log in first!" + Style.RESET_ALL)
        elif choice == '5':
            if current_user:
                current_user = None
                print(Fore.GREEN + "Logged out successfully." + Style.RESET_ALL)
            else:
                print(Fore.RED + "You are not logged in." + Style.RESET_ALL)
        elif choice == '6':
            print(Fore.CYAN + "Goodbye!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Invalid option. Please try again." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
