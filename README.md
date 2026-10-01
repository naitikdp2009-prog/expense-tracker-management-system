# EXPENSE TRACKER MANAGEMENT SYSTEM

A complete, production-grade, modern personal finance web application built for **College Minor Project Review-2**. The system allows users to record, categorize, analyze, and manage personal expenses, set category-wise budgets, visualize spending trends with interactive Chart.js charts, receive smart alerts, run what-if simulations, consult an AI purchase advisor, parse receipt text, and ask questions to a financial chatbot assistant.

---

## 🚀 Key Features & Modules

1. **Financial Dashboard**: Real-time summary cards (Total Income, Total Expenses, Current Balance, Monthly Budget, Remaining Budget, Net Savings), budget progress pacing bar, doughnut category chart, 6-month spending trend, recent transactions table, AI insights, and system alerts.
2. **Add Expense & Voice Entry**: Manual expense form plus hands-free browser Web Speech API voice input (e.g. *"Spent 250 rupees on food"*).
3. **Expense Management**: View all expenses with keyword search, filter by Category, Date range, and Payment method (Cash, UPI, Credit Card, Debit Card, Net Banking), sorting options, and CSV data export.
4. **Income Management**: Record and track income streams, monthly earnings, and historical logs.
5. **Budget Management**: Configure overall monthly budget limits and category-wise spending limits with real-time color-coded progress bars and automated threshold alert warnings (50%, 75%, 90%, 100%+).
6. **Reports & Analytics**: Interactive Chart.js reports for Daily Expenses (14-day bar chart), Income vs Expense comparison line chart, Category distribution, and Monthly Savings trend.
7. **AI-Powered Expense Analysis**: Offline deterministic pattern engine detecting month-over-month category variance, daily burn velocity, and recurring micro-expenses.
8. **Receipt Scanner & OCR**: Image drag-and-drop dropzone, regex heuristic receipt text extractor, and editable correction form.
9. **Smart Purchase Advisor**: Decision matrix giving **BUY**, **WAIT**, or **AVOID** recommendations based on item price, category, urgency, need vs want rating, and budget headroom.
10. **What-If Budget Simulator**: Interactive scenario comparison calculating new monthly spending, remaining budget, usage %, and savings impact before committing to a purchase.
11. **Financial Chat Assistant**: Natural language query engine answering questions like *"How much did I spend this month?"*, *"What is my biggest expense category?"*, *"How much budget is remaining?"*, and *"Can I afford 1500 rupees?"*.
12. **Settings & Demo Data Tools**: Currency symbol selection (₹, $, €, £), Light/Dark theme switch, one-click demo data seeder, and CSV backup.
13. **Minor Project Review-2 Hub**: Dedicated presentation view outlining Problem Statement, Proposed Solution, Data Flow Architecture, Budget Consideration (Free Stack), Development Timeline Plan, Alternative Strategies, and Future Scope.

---

## 🛠 Tech Stack

* **Frontend**: HTML5, CSS3 (Fintech Dark/Light Theme), Vanilla JavaScript, Chart.js, FontAwesome Icons CDN, Web Speech API
* **Backend**: Python 3.x, Flask (RESTful Blueprints)
* **Database**: SQLite 3 (`expense_tracker.db`)

---

## 💻 Installation & Quick Start Guide

### Step 1: Install Dependencies
Ensure Python 3 is installed, then run:
```bash
pip install -r requirements.txt
```

### Step 2: Launch the Application
Run the Flask server:
```bash
python app.py
```

### Step 3: Access in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🗄 Database Architecture (`expense_tracker.db`)

The application automatically creates and initializes SQLite tables on first startup:
* `categories`: Master table for expense categories (`Food`, `Transport`, `Shopping`, `Education`, `Entertainment`, `Bills`, `Healthcare`, `Travel`, `Other`).
* `expenses`: Stores transaction amount, category reference, date, payment method, description, notes.
* `income`: Stores income source, amount, date, description.
* `budgets`: Stores overall and category monthly limits per month/year.
* `alerts`: Stores threshold warnings and anomaly notifications.
* `receipts`: Stores uploaded receipt image metadata and parsed text.
* `user_settings`: Key-value configuration for currency symbol and theme mode.

---

## 🎓 College Minor Project Review-2 Demonstration Guide

During your review presentation:
1. Navigate to **Project Overview** in the left sidebar to present the Problem Statement, Solution Architecture, Budget Consideration, and Development Plan.
2. Click **Settings** -> **Seed / Reset Realistic Demo Data** to populate the dashboard with 30+ realistic transactions.
3. Show the **Dashboard** metrics cards, Chart.js doughnut chart, spending trend line chart, and live budget progress bar.
4. Demonstrate **Voice Expense Entry** by clicking the microphone on **Add Expense** and speaking *"Spent 250 rupees on food"*.
5. Demonstrate **Purchase Advisor** by entering a product (e.g. Smartwatch for ₹3,500) and explaining the BUY/WAIT/AVOID recommendation matrix.
6. Run the **What-If Simulator** to compare CURRENT vs AFTER PURCHASE budget headroom.
7. Interact with the **Chat Assistant** by typing *"What is my biggest expense category?"*.

---

## ☁ Free Cloud Deployment Options

You can deploy this project for free using:
1. **Render.com / Railway.app**: Connect your GitHub repository, set Build Command to `pip install -r requirements.txt` and Start Command to `python app.py` (or `gunicorn app:app`).
2. **PythonAnywhere**: Upload files or clone git repo, configure a Web App pointing to `app.py`.
