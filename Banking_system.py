import sqlite3
import random
import re
import datetime
from getpass import getpass
import sys

# Using SQLite3 due to installation issues in MySQL

class BankingSystem:
    def __init__(self):
        # Connect to db
        self.db = sqlite3.connect('banking_system.db')
        self.db_cur = self.db.cursor()
        self.setup_tables()
        self.logged_user = None


    def setup_tables(self):
        # Make tables if they don't exist
        self.db_cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                acc_num TEXT UNIQUE NOT NULL,
                dob DATE NOT NULL,
                city TEXT NOT NULL,
                pwd TEXT NOT NULL,
                cash_balance REAL NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')

        # Track logins
        self.db_cur.execute('''
            CREATE TABLE IF NOT EXISTS login_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acc_num TEXT NOT NULL,
                login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                logout_time DATETIME,
                FOREIGN KEY (acc_num) REFERENCES users(acc_num)
            )
        ''')


        # Money stuff
        self.db_cur.execute('''
            CREATE TABLE IF NOT EXISTS money_moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acc_num TEXT NOT NULL,
                move_type TEXT NOT NULL,
                amount REAL NOT NULL,
                to_acc TEXT,
                when_moved DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (acc_num) REFERENCES users(acc_num)
            )
        ''')
        
        self.db.commit()


    def check_name(self, name):
        if not name or not re.match("^[A-Za-z ]{2,50}$", name):
            raise ValueError("Bad name! Letters only, 2-50 chars")
        return True

    def check_phone(self, num):
        if not re.match("^[0-9]{10}$", num):
            raise ValueError("Phone number should be 10 digits!")
        return True

    def check_email(self, email):
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("That's not a valid email!")
        return True


    def check_pwd(self, pwd):
        if len(pwd) < 8:
            raise ValueError("Password too short! Need 8+ chars")
        if not re.search("[A-Z]", pwd):
            raise ValueError("Need an uppercase letter!")
        if not re.search("[a-z]", pwd):
            raise ValueError("Need a lowercase letter!")
        if not re.search("[0-9]", pwd):
            raise ValueError("Need a number!")
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", pwd):
            raise ValueError("Need a special character!")
        return True

    def make_acc_num(self):
        while True:
            num = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            self.db_cur.execute("SELECT 1 FROM users WHERE acc_num = ?", (num,))
            if not self.db_cur.fetchone():
                return num


    def add_user(self):
        try:
            print("\n=== Sign Up ===")
            
            name = input("Your name: ")
            self.check_name(name)
            
            dob = input("When were you born? (YYYY-MM-DD): ")
            datetime.datetime.strptime(dob, '%Y-%m-%d')
            
            city = input("Which city?: ")
            if not city:
                raise ValueError("Need a city!")
            
            pwd = getpass("Pick a password: ")
            self.check_pwd(pwd)
            
            cash = float(input("Initial deposit (min 2000): "))
            if cash < 2000:
                raise ValueError("Need at least 2000 to open account!")
            
            phone = input("Your phone number: ")
            self.check_phone(phone)
            
            email = input("Your email: ")
            self.check_email(email)
            
            acc_num = self.make_acc_num()
            
            self.db_cur.execute('''
                INSERT INTO users (name, acc_num, dob, city, pwd, cash_balance, 
                                 phone, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, acc_num, dob, city, pwd, cash, phone, email))
            
            self.db.commit()
            
            print(f"\nWelcome aboard!")
            print(f"Your account number is: {acc_num}")
            
        except Exception as e:
            print(f"Oops: {str(e)}")
            return False
        return True


    def show_users(self):
        self.db_cur.execute("SELECT acc_num, name, city, phone, email, cash_balance FROM users")
        users = self.db_cur.fetchall()
        
        if not users:
            print("\nNo users yet!")
            return
        
        print("\n=== Users List ===")
        print(f"{'Account #':<15} {'Name':<20} {'City':<15} {'Phone':<15} {'Email':<25} {'Balance':<10}")
        print("-" * 100)
        
        for u in users:
            acc, name, city, phone, email, cash = u
            print(f"{acc:<15} {name:<20} {city:<15} {phone:<15} {email:<25} {cash:<10.2f}")


    def login(self):
        try:
            print("\n=== Login ===")
            acc = input("Account number: ")
            pwd = getpass("Password: ")
            
            self.db_cur.execute("""
                SELECT * FROM users 
                WHERE acc_num = ? AND pwd = ?
            """, (acc, pwd))
            
            user = self.db_cur.fetchone()
            if not user:
                print("Wrong account number or password!")
                return False
            
            self.logged_user = user
            
            # Log it
            self.db_cur.execute("""
                INSERT INTO login_info (acc_num) VALUES (?)
            """, (acc,))
            self.db.commit()
            
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def show_balance(self):
        print(f"\nYou have: ${self.logged_user[6]:.2f}")


    def credit_amount(self):
        try:
            amt = float(input("\nHow much to deposit? $"))
            if amt <= 0:
                raise ValueError("Amount needs to be positive!")
            
            new_total = self.logged_user[6] + amt
            
            self.db_cur.execute("""
                UPDATE users 
                SET cash_balance = ? 
                WHERE acc_num = ?
            """, (new_total, self.logged_user[2]))
            
            self.db_cur.execute("""
                INSERT INTO money_moves (acc_num, move_type, amount)
                VALUES (?, 'CREDIT', ?)
            """, (self.logged_user[2], amt))
            
            self.db.commit()
            print(f"Added ${amt:.2f}")
            print(f"New balance: ${new_total:.2f}")
            
            self.logged_user = list(self.logged_user)
            self.logged_user[6] = new_total
            
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Something went wrong: {str(e)}")


    def debit_amount(self):
        try:
            amt = float(input("\nHow much to withdraw? $"))
            if amt <= 0:
                raise ValueError("Amount needs to be positive!")
            
            if amt > self.logged_user[6]:
                raise ValueError("Not enough money!")
            
            if self.logged_user[6] - amt < 2000:
                raise ValueError("Can't go below $2000!")
            
            new_total = self.logged_user[6] - amt
            
            self.db_cur.execute("""
                UPDATE users 
                SET cash_balance = ? 
                WHERE acc_num = ?
            """, (new_total, self.logged_user[2]))
            
            self.db_cur.execute("""
                INSERT INTO money_moves (acc_num, move_type, amount)
                VALUES (?, 'DEBIT', ?)
            """, (self.logged_user[2], amt))
            
            self.db.commit()
            print(f"Withdrew ${amt:.2f}")
            print(f"New balance: ${new_total:.2f}")
            
            self.logged_user = list(self.logged_user)
            self.logged_user[6] = new_total
            
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Something went wrong: {str(e)}")


    def transfer_money(self):
        try:
            to_acc = input("\nAccount number to send to: ")
            
            self.db_cur.execute("SELECT acc_num, name FROM users WHERE acc_num = ?", 
                              (to_acc,))
            receiver = self.db_cur.fetchone()
            
            if not receiver:
                raise ValueError("Account not found!")
            
            if to_acc == self.logged_user[2]:
                raise ValueError("Can't send money to yourself!")
            
            amt = float(input("How much to send? $"))
            if amt <= 0:
                raise ValueError("Amount needs to be positive!")
            
            if amt > self.logged_user[6]:
                raise ValueError("Not enough money!")
            
            if self.logged_user[6] - amt < 2000:
                raise ValueError("Can't go below $2000!")
            
            new_total = self.logged_user[6] - amt
            self.db_cur.execute("""
                UPDATE users 
                SET cash_balance = ? 
                WHERE acc_num = ?
            """, (new_total, self.logged_user[2]))
            
            self.db_cur.execute("""
                UPDATE users 
                SET cash_balance = cash_balance + ? 
                WHERE acc_num = ?
            """, (amt, to_acc))
            
            self.db_cur.execute("""
                INSERT INTO money_moves (acc_num, move_type, amount, to_acc)
                VALUES (?, 'TRANSFER', ?, ?)
            """, (self.logged_user[2], amt, to_acc))
            
            self.db.commit()
            print(f"Sent ${amt:.2f} to account {to_acc}")
            print(f"New balance: ${new_total:.2f}")
            
            self.logged_user = list(self.logged_user)
            self.logged_user[6] = new_total
            
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Transfer failed: {str(e)}")


    def change_pwd(self):
        try:
            old_pwd = getpass("\nCurrent password: ")
            if old_pwd != self.logged_user[5]:
                raise ValueError("Wrong password!")
            
            new_pwd = getpass("New password: ")
            self.check_pwd(new_pwd)
            
            check_pwd = getpass("Type it again: ")
            if new_pwd != check_pwd:
                raise ValueError("Passwords don't match!")
            
            self.db_cur.execute("""
                UPDATE users 
                SET pwd = ? 
                WHERE acc_num = ?
            """, (new_pwd, self.logged_user[2]))
            
            self.db.commit()
            print("Password updated!")
            
            self.logged_user = list(self.logged_user)
            self.logged_user[5] = new_pwd
            
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Couldn't change password: {str(e)}")


    def update_info(self):
        try:
            print("\n=== Update Info ===")
            print("Hit Enter to keep current info")
            
            name = input(f"Name [{self.logged_user[1]}]: ") or self.logged_user[1]
            self.check_name(name)
            
            city = input(f"City [{self.logged_user[4]}]: ") or self.logged_user[4]
            
            phone = input(f"Phone [{self.logged_user[7]}]: ") or self.logged_user[7]
            self.check_phone(phone)
            
            email = input(f"Email [{self.logged_user[8]}]: ") or self.logged_user[8]
            self.check_email(email)
            
            self.db_cur.execute("""
                UPDATE users 
                SET name = ?, city = ?, phone = ?, email = ?
                WHERE acc_num = ?
            """, (name, city, phone, email, self.logged_user[2]))
            
            self.db.commit()
            print("Info updated!")
            
            self.logged_user = list(self.logged_user)
            self.logged_user[1] = name
            self.logged_user[4] = city
            self.logged_user[7] = phone
            self.logged_user[8] = email
            
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Update failed: {str(e)}")


    def logout(self):
        try:
            if self.logged_user:
                self.db_cur.execute("""
                    UPDATE login_info 
                    SET logout_time = CURRENT_TIMESTAMP 
                    WHERE acc_num = ? 
                    AND logout_time IS NULL
                """, (self.logged_user[2],))
                self.db.commit()
                
                self.logged_user = None
                print("\nSee ya!")
                return True
        except Exception as e:
            print(f"Logout problem: {str(e)}")
        return False


    def close_db(self):
        if self.logged_user:
            self.logout()
        self.db.close()


def main():
    bank = BankingSystem()
    
    while True:
        if not bank.logged_user:
            print("\n=== Welcome to the Bank ===")
            print("1. New Account")
            print("2. Show Users")
            print("3. Login")
            print("4. Exit")
            
            choice = input("\nWhat do you want to do? (1-4): ")
            
            if choice == '1':
                bank.add_user()
            elif choice == '2':
                bank.show_users()
            elif choice == '3':
                if bank.login():
                    print("\nYou're in!")
            elif choice == '4':
                print("\nThanks for banking with us!")
                bank.close_db()
                sys.exit(0)
            else:
                print("That's not an option!")
        
        else:
            print(f"\nHi {bank.logged_user[1]}!")
            print("1. Check Balance")
            print("2. Add Money")
            print("3. Get Money")
            print("4. Send Money")
            print("5. Change Password")
            print("6. Update Info")
            print("7. Logout</antArtifact>