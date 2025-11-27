#!/usr/bin/env python3
"""
Pocket Money Tracker - Simple CLI App

Features:
- Add income (pocket money received)
- Add expense (money spent)
- See current balance
- See full transaction history
- See monthly summary

Data is stored in 'pocket_data.json' in the same folder.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

DATA_FILE = "pocket_data.json"


# ---------------------- Data Handling ---------------------- #

def load_data() -> Dict[str, Any]:
    """Load data from JSON file or initialize if not present."""
    if not os.path.exists(DATA_FILE):
        return {
            "starting_balance": 0.0,
            "transactions": []  # list of dicts
        }

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # basic sanity checks
        if "starting_balance" not in data:
            data["starting_balance"] = 0.0
        if "transactions" not in data:
            data["transactions"] = []
        return data
    except (json.JSONDecodeError, OSError):
        print("⚠️ Data file is corrupted or unreadable. Starting fresh.")
        return {
            "starting_balance": 0.0,
            "transactions": []
        }


def save_data(data: Dict[str, Any]) -> None:
    """Save data to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ---------------------- Core Logic ---------------------- #

def calculate_balance(data: Dict[str, Any]) -> float:
    """Calculate current balance from starting balance and all transactions."""
    balance = float(data.get("starting_balance", 0.0))
    for t in data.get("transactions", []):
        amount = float(t.get("amount", 0.0))
        if t.get("type") == "IN":
            balance += amount
        elif t.get("type") == "OUT":
            balance -= amount
    return balance


def print_header(title: str) -> None:
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def input_float(prompt: str) -> float:
    """Robust float input."""
    while True:
        value = input(prompt).strip()
        try:
            amount = float(value)
            return amount
        except ValueError:
            print("❌ Invalid number. Try again.")


def input_date(prompt: str) -> str:
    """
    Ask user for date.
    If user presses Enter, use today's date.
    Format: YYYY-MM-DD
    """
    while True:
        value = input(prompt + " (YYYY-MM-DD, leave empty for today): ").strip()
        if value == "":
            return datetime.today().strftime("%Y-%m-%d")
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD.")


# ---------------------- Menu Actions ---------------------- #

def set_starting_balance(data: Dict[str, Any]) -> None:
    print_header("Set / Update Starting Balance")
    current = float(data.get("starting_balance", 0.0))
    print(f"Current starting balance: ₹{current:.2f}")
    new_balance = input_float("Enter new starting balance (₹): ")
    data["starting_balance"] = float(new_balance)
    save_data(data)
    print(f"✅ Starting balance updated to ₹{new_balance:.2f}")


def add_income(data: Dict[str, Any]) -> None:
    print_header("Add Income (Pocket Money Received)")
    amount = input_float("Amount received (₹): ")
    if amount <= 0:
        print("❌ Amount must be positive.")
        return

    source = input("Source (e.g., 'From Dad', 'Gift', 'Extra work'): ").strip()
    date = input_date("Date")

    transaction = {
        "date": date,
        "type": "IN",
        "amount": amount,
        "category": source if source else "Pocket Money",
        "note": input("Note (optional): ").strip()
    }

    data["transactions"].append(transaction)
    save_data(data)
    print(f"✅ Income of ₹{amount:.2f} added.")


def add_expense(data: Dict[str, Any]) -> None:
    print_header("Add Expense (Money Spent)")
    amount = input_float("Amount spent (₹): ")
    if amount <= 0:
        print("❌ Amount must be positive.")
        return

    category = input("Category (e.g., 'Snacks', 'Movies', 'Games'): ").strip()
    if not category:
        category = "Other"

    date = input_date("Date")

    transaction = {
        "date": date,
        "type": "OUT",
        "amount": amount,
        "category": category,
        "note": input("Note (optional): ").strip()
    }

    data["transactions"].append(transaction)
    save_data(data)
    print(f"✅ Expense of ₹{amount:.2f} added.")


def show_balance(data: Dict[str, Any]) -> None:
    print_header("Current Balance")
    balance = calculate_balance(data)
    print(f"💰 Current balance: ₹{balance:.2f}")
    print(f"📌 Starting balance: ₹{float(data.get('starting_balance', 0.0)):.2f}")
    print(f"🧾 Total transactions: {len(data.get('transactions', []))}")


def list_transactions(data: Dict[str, Any]) -> None:
    print_header("Transaction History")
    transactions: List[Dict[str, Any]] = data.get("transactions", [])

    if not transactions:
        print("No transactions yet.")
        return

    # Sort by date
    transactions_sorted = sorted(transactions, key=lambda x: x.get("date", ""))

    print(f"{'Date':<12} {'Type':<4} {'Amount':>10}  {'Category':<15} Note")
    print("-" * 70)
    for t in transactions_sorted:
        date = t.get("date", "")
        ttype = "IN" if t.get("type") == "IN" else "OUT"
        amount = float(t.get("amount", 0.0))
        category = t.get("category", "")
        note = t.get("note", "")
        sign = "+" if ttype == "IN" else "-"
        print(f"{date:<12} {ttype:<4} {sign}{amount:>9.2f}  {category:<15} {note}")


def monthly_summary(data: Dict[str, Any]) -> None:
    print_header("Monthly Summary")

    year = input("Enter year (YYYY, leave empty for current year): ").strip()
    month = input("Enter month (MM, leave empty for current month): ").strip()

    today = datetime.today()
    if year == "":
        year = today.strftime("%Y")
    if month == "":
        month = today.strftime("%m")

    # Validate year, month
    try:
        datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
    except ValueError:
        print("❌ Invalid year/month.")
        return

    ym_prefix = f"{year}-{month:>02}" if len(month) == 2 else f"{year}-0{month}"

    income_total = 0.0
    expense_total = 0.0
    counted_transactions = []

    for t in data.get("transactions", []):
        date = t.get("date", "")
        if not date.startswith(ym_prefix):
            continue
        amount = float(t.get("amount", 0.0))
        if t.get("type") == "IN":
            income_total += amount
        elif t.get("type") == "OUT":
            expense_total += amount
        counted_transactions.append(t)

    print(f"\nSummary for {year}-{month}:")
    print(f" - Total Income : ₹{income_total:.2f}")
    print(f" - Total Expense: ₹{expense_total:.2f}")
    print(f" - Net Change   : ₹{(income_total - expense_total):.2f}")
    print(f" - Transactions : {len(counted_transactions)}")

    if counted_transactions:
        print("\nDetails:")
        print(f"{'Date':<12} {'Type':<4} {'Amount':>10}  {'Category':<15} Note")
        print("-" * 70)
        for t in sorted(counted_transactions, key=lambda x: x.get("date", "")):
            date = t.get("date", "")
            ttype = t.get("type")
            amount = float(t.get("amount", 0.0))
            category = t.get("category", "")
            note = t.get("note", "")
            sign = "+" if ttype == "IN" else "-"
            print(f"{date:<12} {ttype:<4} {sign}{amount:>9.2f}  {category:<15} {note}")


# ---------------------- Main Menu ---------------------- #

def print_menu() -> None:
    print("\n" + "=" * 50)
    print("📱 Pocket Money Tracker")
    print("=" * 50)
    print("1) Set / Update starting balance")
    print("2) Add income (money received)")
    print("3) Add expense (money spent)")
    print("4) Show current balance")
    print("5) Show all transactions")
    print("6) Show monthly summary")
    print("0) Exit")


def main() -> None:
    data = load_data()

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            set_starting_balance(data)
        elif choice == "2":
            add_income(data)
        elif choice == "3":
            add_expense(data)
        elif choice == "4":
            show_balance(data)
        elif choice == "5":
            list_transactions(data)
        elif choice == "6":
            monthly_summary(data)
        elif choice == "0":
            print("👋 Goodbye! Keep tracking your money wisely.")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()
