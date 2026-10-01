from database.database import get_db_connection
from datetime import datetime, timedelta

def get_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now()
    current_month_str = f"{today.year}-{today.month:02d}"

    # Total Income
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income")
    total_income = cursor.fetchone()[0]

    # Total Expenses
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
    total_expenses = cursor.fetchone()[0]

    # Current Balance
    current_balance = total_income - total_expenses

    # Current Month Expenses
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE strftime('%Y-%m', date) = ?", (current_month_str,))
    monthly_expenses = cursor.fetchone()[0]

    # Current Month Income
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE strftime('%Y-%m', date) = ?", (current_month_str,))
    monthly_income = cursor.fetchone()[0]

    # Monthly Budget (Overall)
    cursor.execute("SELECT monthly_limit FROM budgets WHERE category_id IS NULL AND month = ? AND year = ?",
                   (today.month, today.year))
    row = cursor.fetchone()
    monthly_budget = row['monthly_limit'] if row else 25000.0

    remaining_budget = max(0, monthly_budget - monthly_expenses)
    budget_usage_pct = round((monthly_expenses / monthly_budget * 100), 1) if monthly_budget > 0 else 0

    # Savings calculation
    savings = max(0, total_income - total_expenses)

    conn.close()

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_budget': monthly_budget,
        'remaining_budget': remaining_budget,
        'budget_usage_pct': budget_usage_pct,
        'savings': savings
    }

def get_category_breakdown(period='current_month'):
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now()
    current_month_str = f"{today.year}-{today.month:02d}"

    if period == 'current_month':
        query = """
            SELECT c.name, c.color, c.icon, COALESCE(SUM(e.amount), 0) as total
            FROM categories c
            LEFT JOIN expenses e ON c.id = e.category_id AND strftime('%Y-%m', e.date) = ?
            GROUP BY c.id
            HAVING total > 0
            ORDER BY total DESC
        """
        cursor.execute(query, (current_month_str,))
    else:
        query = """
            SELECT c.name, c.color, c.icon, COALESCE(SUM(e.amount), 0) as total
            FROM categories c
            LEFT JOIN expenses e ON c.id = e.category_id
            GROUP BY c.id
            HAVING total > 0
            ORDER BY total DESC
        """
        cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()

    categories = [row['name'] for row in rows]
    amounts = [row['total'] for row in rows]
    colors = [row['color'] for row in rows]
    icons = [row['icon'] for row in rows]

    return {
        'labels': categories,
        'data': amounts,
        'colors': colors,
        'icons': icons,
        'raw': [dict(row) for row in rows]
    }

def get_monthly_spending_trend(months_count=6):
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now()
    labels = []
    expense_data = []
    income_data = []

    for i in range(months_count - 1, -1, -1):
        # Calculate date for i months ago
        target_date = today.replace(day=1) - timedelta(days=i * 30)
        month_str = f"{target_date.year}-{target_date.month:02d}"
        month_label = target_date.strftime("%b %Y")
        labels.append(month_label)

        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE strftime('%Y-%m', date) = ?", (month_str,))
        exp = cursor.fetchone()[0]
        expense_data.append(exp)

        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE strftime('%Y-%m', date) = ?", (month_str,))
        inc = cursor.fetchone()[0]
        income_data.append(inc)

    conn.close()

    return {
        'labels': labels,
        'expenses': expense_data,
        'income': income_data
    }

def generate_ai_insights():
    """
    Rule-based AI Insight generator for expense analysis.
    Works offline without any paid API keys.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now()
    current_month_str = f"{today.year}-{today.month:02d}"
    
    # Get previous month
    first_of_current = today.replace(day=1)
    prev_month_date = first_of_current - timedelta(days=1)
    prev_month_str = f"{prev_month_date.year}-{prev_month_date.month:02d}"

    insights = []

    # 1. Month-over-month category spending comparison
    cursor.execute("""
        SELECT c.name,
               SUM(CASE WHEN strftime('%Y-%m', e.date) = ? THEN e.amount ELSE 0 END) as curr_amt,
               SUM(CASE WHEN strftime('%Y-%m', e.date) = ? THEN e.amount ELSE 0 END) as prev_amt
        FROM categories c
        JOIN expenses e ON c.id = e.category_id
        GROUP BY c.id
        HAVING curr_amt > 0 OR prev_amt > 0
    """, (current_month_str, prev_month_str))

    cat_diffs = cursor.fetchall()
    top_increase_cat = None
    max_increase_pct = 0

    for row in cat_diffs:
        c_name, curr, prev = row['name'], row['curr_amt'], row['prev_amt']
        if prev > 0:
            pct_change = ((curr - prev) / prev) * 100
            if pct_change > max_increase_pct:
                max_increase_pct = pct_change
                top_increase_cat = (c_name, pct_change, curr - prev)

    if top_increase_cat and max_increase_pct > 10:
        insights.append({
            'type': 'spending_spike',
            'icon': 'fa-chart-line',
            'color': 'warning',
            'title': f'Increased Spending in {top_increase_cat[0]}',
            'text': f"You spent {round(top_increase_cat[1], 1)}% more on {top_increase_cat[0]} this month compared to last month (+₹{round(top_increase_cat[2], 2)})."
        })
    else:
        insights.append({
            'type': 'spending_stable',
            'icon': 'fa-check-circle',
            'color': 'success',
            'title': 'Controlled Spending Pattern',
            'text': 'Your month-over-month spending across major categories remains steady and within normal limits.'
        })

    # 2. Highest Spending Category Insight
    cursor.execute("""
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE strftime('%Y-%m', e.date) = ?
        GROUP BY c.id
        ORDER BY total DESC
        LIMIT 1
    """, (current_month_str,))
    top_cat = cursor.fetchone()

    if top_cat:
        insights.append({
            'type': 'top_category',
            'icon': 'fa-crown',
            'color': 'info',
            'title': f'Top Category: {top_cat["name"]}',
            'text': f"{top_cat['name']} is your highest expense category this month, accounting for ₹{round(top_cat['total'], 2)} of total expenses."
        })

    # 3. Budget Velocity & Savings Recommendation
    summary = get_dashboard_summary()
    if summary['monthly_budget'] > 0:
        day_of_month = today.day
        expected_usage_pct = (day_of_month / 30) * 100
        actual_usage_pct = summary['budget_usage_pct']

        if actual_usage_pct > expected_usage_pct + 15:
            insights.append({
                'type': 'budget_pacing',
                'icon': 'fa-exclamation-triangle',
                'color': 'danger',
                'title': 'High Budget Burn Rate',
                'text': f"You have consumed {actual_usage_pct}% of your budget by day {day_of_month} of the month. Consider cutting down on non-essential Shopping or Entertainment."
            })
        elif actual_usage_pct < expected_usage_pct - 10:
            insights.append({
                'type': 'budget_pacing',
                'icon': 'fa-piggy-bank',
                'color': 'success',
                'title': 'Great Savings Velocity',
                'text': f"You are spending below your estimated daily budget velocity. You are on track to save approximately ₹{round(summary['remaining_budget'] * 0.4, 2)} this month!"
            })

    # 4. Frequent Micro-expenses
    cursor.execute("""
        SELECT description, COUNT(*) as cnt, SUM(amount) as total
        FROM expenses
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY LOWER(description)
        HAVING cnt >= 2
        ORDER BY cnt DESC
        LIMIT 1
    """, (current_month_str,))
    freq = cursor.fetchone()

    if freq:
        insights.append({
            'type': 'frequent_expense',
            'icon': 'fa-redo',
            'color': 'primary',
            'title': f'Recurring Small Expense: "{freq["description"]}"',
            'text': f"You purchased '{freq['description']}' {freq['cnt']} times this month (totaling ₹{round(freq['total'], 2)}). Small recurring transactions add up fast!"
        })

    conn.close()
    return insights
