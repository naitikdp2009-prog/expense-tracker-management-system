import sqlite3
import os
from datetime import datetime, timedelta
import random
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def seed_demo_data(force=False):
    """
    Seeds realistic sample data for Minor Project Review-2 presentation.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if not force:
        cursor.execute("SELECT COUNT(*) FROM expenses")
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return "Database already contains data."

    # Clear existing transactional data if force=True
    if force:
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM income")
        cursor.execute("DELETE FROM budgets")
        cursor.execute("DELETE FROM alerts")
        cursor.execute("DELETE FROM receipts")

    today = datetime.now()
    current_month = today.month
    current_year = today.year
    prev_month = (today.replace(day=1) - timedelta(days=1)).month
    prev_year = (today.replace(day=1) - timedelta(days=1)).year

    # 1. Seed Income
    incomes = [
        ("Monthly Allowance / Internship Stipend", 25000.00, f"{current_year}-{current_month:02d}-01", "Fixed monthly stipend"),
        ("Freelance Project Work", 8500.00, f"{current_year}-{current_month:02d}-10", "Web development gig"),
        ("Parental Contribution / Savings Transfer", 5000.00, f"{current_year}-{current_month:02d}-15", "Support allowance"),
        ("Previous Month Stipend", 25000.00, f"{prev_year}-{prev_month:02d}-01", "Stipend for previous month"),
        ("Part-time Tutoring", 4000.00, f"{prev_year}-{prev_month:02d}-12", "Math tutoring fee")
    ]
    for inc in incomes:
        cursor.execute(
            "INSERT INTO income (source, amount, date, description) VALUES (?, ?, ?, ?)",
            inc
        )

    # 2. Seed Budgets for Current Month
    # Category IDs: 1: Food, 2: Transport, 3: Shopping, 4: Education, 5: Entertainment, 6: Bills, 7: Healthcare, 8: Travel, 9: Other
    cursor.execute("INSERT OR REPLACE INTO budgets (category_id, monthly_limit, month, year) VALUES (?, ?, ?, ?)",
                   (None, 24000.00, current_month, current_year)) # Overall budget
    cursor.execute("INSERT OR REPLACE INTO budgets (category_id, monthly_limit, month, year) VALUES (?, ?, ?, ?)",
                   (1, 6000.00, current_month, current_year)) # Food
    cursor.execute("INSERT OR REPLACE INTO budgets (category_id, monthly_limit, month, year) VALUES (?, ?, ?, ?)",
                   (2, 3000.00, current_month, current_year)) # Transport
    cursor.execute("INSERT OR REPLACE INTO budgets (category_id, monthly_limit, month, year) VALUES (?, ?, ?, ?)",
                   (3, 4000.00, current_month, current_year)) # Shopping
    cursor.execute("INSERT OR REPLACE INTO budgets (category_id, monthly_limit, month, year) VALUES (?, ?, ?, ?)",
                   (4, 3500.00, current_month, current_year)) # Education
    cursor.execute("INSERT OR REPLACE INTO budgets (category_id, monthly_limit, month, year) VALUES (?, ?, ?, ?)",
                   (5, 2500.00, current_month, current_year)) # Entertainment
    cursor.execute("INSERT OR REPLACE INTO budgets (category_id, monthly_limit, month, year) VALUES (?, ?, ?, ?)",
                   (6, 3000.00, current_month, current_year)) # Bills

    # 3. Seed Realistic Expenses (Current and Previous Month)
    sample_expenses = [
        # Current month expenses
        (450.00, 1, (today - timedelta(days=1)).strftime("%Y-%m-%d"), "College Canteen Lunch", "UPI", "Lunch with classmates"),
        (120.00, 2, (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Bus Pass & Metro Recharge", "UPI", "Weekly commute"),
        (1850.00, 4, (today - timedelta(days=2)).strftime("%Y-%m-%d"), "Python & Data Science Books", "Debit Card", "Reference textbooks for minor project"),
        (2500.00, 6, (today - timedelta(days=3)).strftime("%Y-%m-%d"), "Hostel Electricity & Wi-Fi Bill", "Net Banking", "Monthly utility dues"),
        (1290.00, 3, (today - timedelta(days=4)).strftime("%Y-%m-%d"), "New Sneakers from Mall", "Credit Card", "Discounted sale purchase"),
        (350.00, 5, (today - timedelta(days=5)).strftime("%Y-%m-%d"), "Movie Ticket & Snacks", "UPI", "Weekend movie show"),
        (680.00, 1, (today - timedelta(days=6)).strftime("%Y-%m-%d"), "Grocery Shopping at Supermarket", "UPI", "Snacks, milk and fruits"),
        (250.00, 2, (today - timedelta(days=7)).strftime("%Y-%m-%d"), "Auto Rickshaw Fare", "Cash", "Travel to project lab"),
        (499.00, 6, (today - timedelta(days=8)).strftime("%Y-%m-%d"), "Mobile Recharge Unlimited Plan", "UPI", "Monthly 5G pack"),
        (850.00, 7, (today - timedelta(days=9)).strftime("%Y-%m-%d"), "Doctor Consultation & Medicines", "UPI", "Flu checkup"),
        (320.00, 1, (today - timedelta(days=10)).strftime("%Y-%m-%d"), "Dinner at Pizza Corner", "UPI", "Group study dinner"),
        (1400.00, 3, (today - timedelta(days=12)).strftime("%Y-%m-%d"), "College Backpack", "Credit Card", "Durable bag for laptop"),
        (600.00, 4, (today - timedelta(days=14)).strftime("%Y-%m-%d"), "Project Printing & Binding", "Cash", "Minor Project Review-1 documentation"),
        (2200.00, 8, (today - timedelta(days=16)).strftime("%Y-%m-%d"), "Train Ticket Home", "Net Banking", "Festival weekend trip"),
        (300.00, 1, (today - timedelta(days=18)).strftime("%Y-%m-%d"), "Cafeteria Coffee & Muffins", "UPI", "Evening break"),
        (1500.00, 5, (today - timedelta(days=20)).strftime("%Y-%m-%d"), "Gaming Zone Pass & Gaming", "UPI", "Outing with roommates"),
        (950.00, 1, (today - timedelta(days=22)).strftime("%Y-%m-%d"), "Departmental Party Contribution", "UPI", "Senior farewell party"),
        
        # Previous Month Expenses
        (4200.00, 1, (today - timedelta(days=35)).strftime("%Y-%m-%d"), "Monthly Mess Bill", "UPI", "Regular mess meals"),
        (2200.00, 6, (today - timedelta(days=38)).strftime("%Y-%m-%d"), "Hostel Fee Part Payment", "Net Banking", "Room maintenance"),
        (3100.00, 3, (today - timedelta(days=40)).strftime("%Y-%m-%d"), "Clothes Shopping", "Credit Card", "Festival clothes"),
        (1100.00, 2, (today - timedelta(days=42)).strftime("%Y-%m-%d"), "Cab Rides", "UPI", "Late night hackathon commute"),
        (900.00, 4, (today - timedelta(days=45)).strftime("%Y-%m-%d"), "Online Certification Exam", "Credit Card", "Udemy Python course")
    ]

    for exp in sample_expenses:
        cursor.execute(
            "INSERT INTO expenses (amount, category_id, date, description, payment_method, notes) VALUES (?, ?, ?, ?, ?, ?)",
            exp
        )

    # 4. Seed Smart Alerts
    cursor.execute("""
        INSERT INTO alerts (alert_type, message, severity) VALUES 
        ('budget_warning', 'Food category budget has reached 72% usage (₹4,320 / ₹6,000).', 'warning'),
        ('budget_info', 'Overall monthly budget is on track (62% used).', 'info'),
        ('spending_anomaly', 'High expenditure detected in Education category (₹2,450 this week).', 'warning'),
        ('budget_danger', 'Shopping budget limit reached 85%. Consider holding non-essential purchases.', 'danger')
    """)

    conn.commit()
    conn.close()
    return "Database seeded successfully with realistic demo data!"
