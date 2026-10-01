from flask import Blueprint, render_template, jsonify, request
from database.database import get_db_connection
from services.analytics import get_category_breakdown, get_monthly_spending_trend
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
def reports_view():
    return render_template('reports.html')

@reports_bp.route('/api/reports/analytics')
def reports_analytics_api():
    period = request.args.get('period', 'monthly') # 'daily', 'weekly', 'monthly', 'all'
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now()

    # 1. Income vs Expense Comparison
    trend_data = get_monthly_spending_trend(6)

    # 2. Savings Trend
    savings_trend = []
    for i in range(len(trend_data['income'])):
        inc = trend_data['income'][i]
        exp = trend_data['expenses'][i]
        savings_trend.append(max(0, inc - exp))

    # 3. Daily Expenses (Last 14 days)
    daily_labels = []
    daily_expenses = []
    for d in range(13, -1, -1):
        dt = today - timedelta(days=d)
        d_str = dt.strftime('%Y-%m-%d')
        daily_labels.append(dt.strftime('%b %d'))

        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE date = ?", (d_str,))
        daily_expenses.append(cursor.fetchone()[0])

    # 4. Top Spending Categories
    cursor.execute("""
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        GROUP BY c.id
        ORDER BY total DESC
        LIMIT 5
    """)
    top_categories = [dict(row) for row in cursor.fetchall()]

    conn.close()

    category_data = get_category_breakdown('all' if period == 'all' else 'current_month')

    return jsonify({
        'trend': trend_data,
        'savings_trend': savings_trend,
        'daily': {
            'labels': daily_labels,
            'expenses': daily_expenses
        },
        'category': category_data,
        'top_categories': top_categories
    })
