import re
from database.database import get_db_connection
from services.analytics import get_dashboard_summary, get_category_breakdown
from datetime import datetime

def process_chat_message(user_message):
    """
    Rule-based Natural Language Processing engine for Financial Assistant.
    Parses intent, queries SQLite DB, and returns structured response.
    """
    msg = user_message.strip().lower()
    summary = get_dashboard_summary()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Monthly Spending Query
    if any(kw in msg for kw in ['how much did i spend', 'monthly expense', 'total spent', 'spending this month']):
        reply = f"You have spent **₹{summary['monthly_expenses']:,.2f}** so far this month out of your overall budget of **₹{summary['monthly_budget']:,.2f}** ({summary['budget_usage_pct']}% used)."
        return {
            'reply': reply,
            'intent': 'monthly_spending',
            'data': summary
        }

    # 2. Remaining Budget Query
    elif any(kw in msg for kw in ['remaining budget', 'budget left', 'how much budget', 'budget status']):
        reply = f"Your remaining overall budget for this month is **₹{summary['remaining_budget']:,.2f}** (out of **₹{summary['monthly_budget']:,.2f}**)."
        return {
            'reply': reply,
            'intent': 'remaining_budget',
            'data': {'remaining_budget': summary['remaining_budget'], 'monthly_budget': summary['monthly_budget']}
        }

    # 3. Biggest Expense Category Query
    elif any(kw in msg for kw in ['biggest expense', 'highest category', 'most spent on', 'top category', 'largest spending']):
        cat_data = get_category_breakdown('current_month')
        if cat_data['data'] and len(cat_data['data']) > 0:
            top_cat = cat_data['labels'][0]
            top_amt = cat_data['data'][0]
            reply = f"Your highest expense category this month is **{top_cat}** with a total expenditure of **₹{top_amt:,.2f}**."
        else:
            reply = "You haven't recorded any expenses for this month yet."
        return {
            'reply': reply,
            'intent': 'top_category',
            'data': cat_data
        }

    # 4. Total Income Query
    elif any(kw in msg for kw in ['total income', 'income this month', 'how much income', 'how much i earn']):
        reply = f"Your total recorded income is **₹{summary['total_income']:,.2f}**, with **₹{summary['monthly_income']:,.2f}** received this month."
        return {
            'reply': reply,
            'intent': 'income_summary',
            'data': summary
        }

    # 5. Recent Expenses Query
    elif any(kw in msg for kw in ['recent expenses', 'last expenses', 'show expenses', 'recent transactions']):
        cursor.execute("""
            SELECT e.amount, e.date, e.description, c.name as category_name
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            ORDER BY e.date DESC, e.id DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        conn.close()

        if rows:
            items_str = "\n".join([f"• **{r['description']}** ({r['category_name']}): ₹{r['amount']:,.2f} on {r['date']}" for r in rows])
            reply = f"Here are your 5 most recent expenses:\n\n{items_str}"
        else:
            reply = "No recent expenses found."
        return {
            'reply': reply,
            'intent': 'recent_expenses',
            'data': [dict(r) for r in rows] if rows else []
        }

    # 6. Specific Category Spending Query (e.g. "How much did I spend on Food?")
    elif any(kw in msg for kw in ['food', 'transport', 'shopping', 'education', 'entertainment', 'bills', 'healthcare', 'travel']):
        category_match = None
        for cat in ['Food', 'Transport', 'Shopping', 'Education', 'Entertainment', 'Bills', 'Healthcare', 'Travel']:
            if cat.lower() in msg:
                category_match = cat
                break

        if category_match:
            cursor.execute("""
                SELECT COALESCE(SUM(e.amount), 0)
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE LOWER(c.name) = ? AND strftime('%Y-%m', e.date) = strftime('%Y-%m', 'now')
            """, (category_match.lower(),))
            cat_sum = cursor.fetchone()[0]
            conn.close()

            reply = f"You have spent **₹{cat_sum:,.2f}** on **{category_match}** this month."
            return {
                'reply': reply,
                'intent': 'category_specific',
                'category': category_match,
                'amount': cat_sum
            }

    # 7. Affordability Check Query (e.g. "Can I afford 2000 rupees?")
    elif 'afford' in msg or 'can i buy' in msg or 'spend' in msg:
        match = re.search(r'(\d+)', msg)
        if match:
            amount_requested = float(match.group(1))
            rem = summary['remaining_budget']
            if amount_requested <= rem:
                reply = f"Yes! You can afford **₹{amount_requested:,.2f}**. You currently have **₹{rem:,.2f}** remaining in your monthly budget."
            else:
                reply = f"Caution! Spending **₹{amount_requested:,.2f}** would exceed your remaining monthly budget (₹{rem:,.2f}) by ₹{(amount_requested - rem):,.2f}."
            return {
                'reply': reply,
                'intent': 'affordability',
                'amount_requested': amount_requested,
                'remaining': rem
            }

    # 8. Help / General Fallback
    conn.close()
    reply = ("I am your Financial Assistant! You can ask me questions like:\n"
             "• *How much did I spend this month?*\n"
             "• *What is my remaining budget?*\n"
             "• *What is my biggest expense category?*\n"
             "• *Show my recent expenses*\n"
             "• *How much did I spend on Food?*\n"
             "• *Can I afford 1500 rupees?*")
    
    return {
        'reply': reply,
        'intent': 'general_help'
    }
