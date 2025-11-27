#!/usr/bin/env python3
"""
Very Simple Pocket Money Tracker (CLI)

Features:
- Add income
- Add expense
- Show balance
- Show history

Data is stored in 'pocket_money_data.json' in the same folder.
No fancy stuff. Just works.
"""

import json
import os
from datetime import datetime

DATA_FILE = "pocket_money_data.json"


# ---------- Data Handling ---------- #

def load_data():
    """Load existing data or create a new structure."""
    if not os.path.exists(DATA_FILE):
        return {
            "transactions": []  # each: {date, type, amount, note}
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Data file corrupted. Starting fresh.")
        return {"transactions": []}


def save_data(data):
    """Save data to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ---------- Core Logic ---------- #

def calc_balance(data):
    """Return current balance = income - expense."""
    balance = 0.0
    for t in data["transactions"]:
        amt = float(t["amount"])
        if t["type"] == "IN":
            balance += amt
        else:
            balance -= amt
    return balance


def input_float(prompt):
    """Force user to enter a valid number."""
    while True:
        value = input(prompt).strip()
        try:
            num = float(value)
            return num
        except ValueError:
            print("Invalid number. Try again.")


def add_income(data):
    print("\n--- Add Income ---")
    amount = input_float("Amount received (₹): ")
    if amount <= 0:
        print("Amount must be positive.")
        return
    note = input("Note (e.g., from dad, gift, etc.): ").strip()
    if not note:
        note = "Income"
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": "IN",
        "amount": amount,
        "note": note
    }
    data["transactions"].append(transaction)
    save_data(data)
    print("Income added.")


def add_expense(data):
    print("\n--- Add Expense ---")
    amount = input_float("Amount spent (₹): ")
    if amount <= 0:
        print("Amount must be positive.")
        return
    note = input("Note (e.g., snacks, movie, etc.): ").strip()
    if not note:
        note = "Expense"
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": "OUT",
        "amount": amount,
        "note": note
    }
    data["transactions"].append(transaction)
    save_data(data)
    print("Expense added.")


def show_balance(data):
    print("\n--- Current Balance ---")
    balance = calc_balance(data)
    print(f"Balance: ₹{balance:.2f}")
    print(f"Total entries: {len(data['transactions'])}")


def show_history(data):
    print("\n--- Transaction History ---")
    if not data["transactions"]:
        print("No transactions yet.")
        return

    print(f"{'Date':<17} {'Type':<6} {'Amount':>10}  Note")
    print("-" * 50)
    for t in data["transactions"]:
        t_type = "IN" if t["type"] == "IN" else "OUT"
        sign = "+" if t_type == "IN" else "-"
        print(f"{t['date']:<17} {t_type:<6} {sign}{t['amount']:>9.2f}  {t['note']}")


# ---------- Menu ---------- #

def print_menu():
    print("\n==============================")
    print(" Simple Pocket Money Tracker ")
    print("==============================")
    print("1) Add income")
    print("2) Add expense")
    print("3) Show balance")
    print("4) Show history")
    print("0) Exit")


def main():
    data = load_data()

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_income(data)
        elif choice == "2":
            add_expense(data)
        elif choice == "3":
            show_balance(data)
        elif choice == "4":
            show_history(data)
        elif choice == "0":
            print("Exiting. Track your money like an adult.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
