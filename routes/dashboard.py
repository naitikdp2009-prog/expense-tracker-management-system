from flask import Blueprint, render_template, jsonify
from database.database import get_db_connection
from services.analytics import get_dashboard_summary, get_category_breakdown, get_monthly_spending_trend, generate_ai_insights
from services.budget_alerts import evaluate_budget_alerts

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard_view():
    summary = get_dashboard_summary()
    insights = generate_ai_insights()
    alerts = evaluate_budget_alerts()

    # Get recent transactions (top 8)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.amount, e.date, e.description, e.payment_method, c.name as category_name, c.icon, c.color
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC, e.id DESC
        LIMIT 8
    """)
    recent_transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template(
        'dashboard.html',
        summary=summary,
        insights=insights,
        alerts=alerts,
        recent_transactions=recent_transactions
    )

@dashboard_bp.route('/api/dashboard/charts')
def dashboard_charts_api():
    category_data = get_category_breakdown('current_month')
    trend_data = get_monthly_spending_trend(6)
    return jsonify({
        'category': category_data,
        'trend': trend_data
    })
