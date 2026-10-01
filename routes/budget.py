from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.database import get_db_connection
from services.budget_alerts import evaluate_budget_alerts
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET', 'POST'])
def manage_budget():
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now()
    month = today.month
    year = today.year
    month_str = f"{year}-{month:02d}"

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'set_overall':
            overall_limit = float(request.form['overall_limit'])
            cursor.execute("""
                INSERT INTO budgets (category_id, monthly_limit, month, year)
                VALUES (NULL, ?, ?, ?)
                ON CONFLICT(category_id, month, year) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """, (overall_limit, month, year))

        elif action == 'set_category':
            category_id = int(request.form['category_id'])
            category_limit = float(request.form['category_limit'])
            cursor.execute("""
                INSERT INTO budgets (category_id, monthly_limit, month, year)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(category_id, month, year) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """, (category_id, category_limit, month, year))

        conn.commit()
        evaluate_budget_alerts()
        flash('Budget limits updated successfully!', 'success')
        return redirect(url_for('budget.manage_budget'))

    # Retrieve overall budget limit
    cursor.execute("SELECT monthly_limit FROM budgets WHERE category_id IS NULL AND month = ? AND year = ?", (month, year))
    row = cursor.fetchone()
    overall_limit = row['monthly_limit'] if row else 25000.0

    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE strftime('%Y-%m', date) = ?", (month_str,))
    overall_spent = cursor.fetchone()[0]

    overall_remaining = max(0, overall_limit - overall_spent)
    overall_pct = round((overall_spent / overall_limit * 100), 1) if overall_limit > 0 else 0

    # Retrieve category-wise budget limits & current spent
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(c) for c in cursor.fetchall()]

    category_budgets = []
    for c in categories:
        cat_id = c['id']
        cursor.execute("SELECT monthly_limit FROM budgets WHERE category_id = ? AND month = ? AND year = ?", (cat_id, month, year))
        brow = cursor.fetchone()
        limit = brow['monthly_limit'] if brow else 0.0

        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE category_id = ? AND strftime('%Y-%m', date) = ?", (cat_id, month_str))
        spent = cursor.fetchone()[0]

        remaining = max(0, limit - spent) if limit > 0 else 0
        pct = round((spent / limit * 100), 1) if limit > 0 else 0

        status_class = 'success'
        if pct >= 100:
            status_class = 'danger'
        elif pct >= 90:
            status_class = 'danger'
        elif pct >= 75:
            status_class = 'warning'
        elif pct >= 50:
            status_class = 'info'

        category_budgets.append({
            'category_id': cat_id,
            'name': c['name'],
            'icon': c['icon'],
            'color': c['color'],
            'limit': limit,
            'spent': spent,
            'remaining': remaining,
            'pct': pct,
            'status_class': status_class
        })

    conn.close()

    return render_template(
        'budget.html',
        overall_limit=overall_limit,
        overall_spent=overall_spent,
        overall_remaining=overall_remaining,
        overall_pct=overall_pct,
        category_budgets=category_budgets,
        categories=categories,
        month_name=today.strftime('%B %Y')
    )
