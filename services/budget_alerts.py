from database.database import get_db_connection
from datetime import datetime

def evaluate_budget_alerts():
    """
    Evaluates current month budget usage against thresholds (50%, 75%, 90%, 100%+)
    and inserts smart alert records into the alerts table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now()
    month = today.month
    year = today.year
    month_str = f"{year}-{month:02d}"

    # Get all budget rules for the month
    cursor.execute("""
        SELECT b.id, b.category_id, b.monthly_limit, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.month = ? AND b.year = ?
    """, (month, year))
    budgets = cursor.fetchall()

    new_alerts = []

    for b in budgets:
        cat_id = b['category_id']
        cat_name = b['category_name'] if cat_id else "Overall Budget"
        limit = b['monthly_limit']

        if limit <= 0:
            continue

        # Compute spent amount
        if cat_id is None:
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE strftime('%Y-%m', date) = ?", (month_str,))
        else:
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE category_id = ? AND strftime('%Y-%m', date) = ?", (cat_id, month_str))
        
        spent = cursor.fetchone()[0]
        usage_pct = (spent / limit) * 100

        # Determine alert level
        if usage_pct >= 100:
            severity = 'danger'
            alert_type = 'budget_exceeded'
            msg = f"CRITICAL: {cat_name} has exceeded its budget limit! Spent: ₹{spent:,.2f} / ₹{limit:,.2f} ({round(usage_pct, 1)}%)."
        elif usage_pct >= 90:
            severity = 'danger'
            alert_type = 'budget_high_warning'
            msg = f"HIGH ALERT: {cat_name} is at {round(usage_pct, 1)}% of limit! Spent: ₹{spent:,.2f} / ₹{limit:,.2f}."
        elif usage_pct >= 75:
            severity = 'warning'
            alert_type = 'budget_warning'
            msg = f"WARNING: {cat_name} has reached {round(usage_pct, 1)}% usage (₹{spent:,.2f} / ₹{limit:,.2f})."
        elif usage_pct >= 50:
            severity = 'info'
            alert_type = 'budget_info'
            msg = f"NOTICE: {cat_name} budget is 50% consumed (₹{spent:,.2f} / ₹{limit:,.2f})."
        else:
            continue

        # Check if alert already exists recently to prevent duplicates
        cursor.execute("""
            SELECT id FROM alerts 
            WHERE message LIKE ? AND DATE(created_at) = DATE('now')
        """, (f"%{cat_name}%",))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO alerts (alert_type, message, severity, is_read)
                VALUES (?, ?, ?, 0)
            """, (alert_type, msg, severity))
            new_alerts.append(msg)

    conn.commit()

    # Retrieve all recent unread alerts
    cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 10")
    all_alerts = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return all_alerts
