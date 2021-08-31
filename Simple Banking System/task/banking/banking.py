from random import randint
import sqlite3


class BankingSystem:
    count = 0
    bin = '400000'

    def __new__(cls):
        if BankingSystem.count == 0:
            BankingSystem.count += 1
            return object.__new__(cls)

    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS card (
                                id INTEGER PRIMARY KEY,
                                number TEXT,
                                pin TEXT,
                                balance INTEGER DEFAULT 0);""")
        self.conn.commit()

    def create_account(self):
        number, pin = self.generate_card_num()
        self.cur.execute("INSERT INTO card (number, pin) VALUES (?, ?);", (number, pin))
        self.conn.commit()
        print("\nYour card has been created")
        print(f"Your card number:\n{number}\nYour card PIN:\n{pin}\n")

    def generate_card_num(self):
        num = [int(i) for i in BankingSystem.bin] + [randint(0, 9) for _ in range(9)]
        num = ''.join([str(i) for i in self.luhn_algorithm(num)])
        pin = ''.join([str(randint(0, 9)) for _ in range(4)])
        return num, pin

    @staticmethod
    def luhn_algorithm(num):
        temp_num = num[:]
        for i in range(len(temp_num)):
            if (i + 1) % 2 != 0:
                temp_num[i] *= 2
            if temp_num[i] > 9:
                temp_num[i] -= 9
        last_digit = sum(temp_num) % 10
        num.append(10 - last_digit if last_digit != 0 else 0)
        return num

    def login(self):
        num = input("\nEnter your card number:\n")
        pin = input("Enter your PIN:\n")
        self.cur.execute("SELECT number, pin FROM card WHERE number = ? AND pin = ?;", (num, pin))

        if (num, pin) == self.cur.fetchone():
            print("\nYou have successfully logged in!\n")
            self.account(num, pin)
        else:
            print("\nWrong card number or PIN!\n")
            return

    def print_balance(self, num):
        self.cur.execute("SELECT balance FROM card WHERE number=:card_num;", {"card_num": num})
        print(f"\nBalance: {self.cur.fetchone()[0]}\n")

    def add_income(self, num):
        income = int(input('\nEnter income:\n'))
        self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (income, num))
        self.conn.commit()
        print("Income was added!\n")

    def do_transfer(self, num):
        other_num = [int(i) for i in input("\nTransfer\nEnter card number:\n")]
        temp_num = other_num[:]
        temp_num.pop()
        if self.luhn_algorithm(temp_num) != other_num:
            print("Probably you made a mistake in the card number. Please try again!\n")
            return
        other_num = ''.join([str(i) for i in other_num])
        if other_num == num:
            print("You can't transfer money to the same account!\n")
            return
        self.cur.execute("SELECT number FROM card WHERE number=:card_num;", {"card_num": other_num})
        if self.cur.fetchone() is None:
            print("Such a card does not exist.\n")
            return
        money = int(input("Enter how much money you want to transfer:\n"))
        self.cur.execute("SELECT balance FROM card WHERE number=:card_num;", {"card_num": num})
        if money > self.cur.fetchone()[0]:
            print("Not enough money!\n")
            return
        self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (money, other_num))
        self.conn.commit()
        self.cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?;", (money, num))
        self.conn.commit()
        print("Success!\n")

    def close_account(self, num):
        self.cur.execute(f"DELETE FROM card WHERE number=:card_num;", {"card_num": num})
        self.conn.commit()
        print('\nThe account has been closed!\n')

    def account(self, num, pin):
        while True:
            option = input("""1. Balance\n2. Add income\n3. Do transfer
4. Close account\n5. Log out\n0. Exit\n""")
            if option == '1':
                self.print_balance(num)
            elif option == '2':
                self.add_income(num)
            elif option == '3':
                self.do_transfer(num)
            elif option == '4':
                self.close_account(num)
                return
            elif option == '5':
                print("\nYou have successfully logged out!\n")
                return
            elif option == '0':
                print("\nBye!")
                exit()

    def work(self):
        while True:
            option = input("1. Create an account\n2. Log into account\n0. Exit\n")
            if option == '1':
                self.create_account()
            elif option == '2':
                self.login()
            elif option == '0':
                print("\nBye!")
                exit()


bank = BankingSystem()
bank.work()
