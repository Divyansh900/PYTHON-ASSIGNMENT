import sqlite3 as sql
from getpass import getpass

# SQLite3 is used here due to issues with MySQL installation 


conn = sql.connect("banking_system.db")
db_curs = conn.cursor()


db_curs.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Uid TEXT UNIQUE NOT NULL,
    PW TEXT NOT NULL,
    balance REAL DEFAULT 0.0
)
""")
conn.commit()


def register():
    print("\n--- Register ---")
    Uid = input("Enter username : ")
    PW = getpass("Enter password : ")

    try:
        db_curs.execute("INSERT INTO users (Uid, PW) VALUES (?, ?)", (Uid, PW))
        conn.commit()
        print("Registration successful!\n")
    except sql.IntegrityError:
        print("Username already exists. Try again.\n")


def login():
    print("\n--- Login ---")
    Uid = input("Enter your username: ")
    PW = getpass("Enter your password: ")

    db_curs.execute("SELECT * FROM users WHERE Uid = ? AND PW = ?", (Uid, PW))
    user = db_curs.fetchone()

    if user:
        print(f"Welcome, {Uid}!\n")
        return user
    else:
        print("Invalid username or password.\n")
        return None


def deposit(user_id):

    print("\n--- Deposit ---")
    amount = float(input("Enter amount to deposit: "))

    db_curs.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
    conn.commit()

    print(f"Deposited {amount} successfully!\n")


def withdraw(user_id):
    print("\n--- Withdraw ---")
    amount = float(input("Enter amount to withdraw: "))

    db_curs.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    bal = db_curs.fetchone()[0]

    if amount > bal:
        print("Insufficient funds.\n")
    else:
        db_curs.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user_id))
        conn.commit()
        print(f"Withdrew {amount} successfully!\n")


def balance(user_id):
    print("\n--- Check Balance ---")

    db_curs.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    bal = db_curs.fetchone()[0]

    print(f"Your current balance is: {bal}\n")


def menu():

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            user = login()

            if user:
                user_id = user[0]

                while True:
                    print("\n1. Deposit\n2. Withdraw\n3. Check Balance\n4. Logout")
                    user_choice = input("Welcome\nPlease Enter your choice :  ")

                    if user_choice == "1":
                        deposit(user_id)

                    elif user_choice == "2":
                        withdraw(user_id)

                    elif user_choice == "3":
                        balance(user_id)

                    elif user_choice == "4":
                        print("..logged out..\n\n")
                        break

                    else:
                        print("Please enter a valid choice\n")


        elif choice == "3":
            print("Exiting...\n")
            break

        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    print('Banking System with SQL\n')
    menu()