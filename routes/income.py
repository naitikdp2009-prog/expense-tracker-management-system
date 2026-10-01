from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.database import get_db_connection
from datetime import datetime

income_bp = Blueprint('income', __name__)

@income_bp.route('/income', methods=['GET', 'POST'])
def manage_income():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        source = request.form['source'].strip()
        amount = float(request.form['amount'])
        date = request.form['date']
        description = request.form.get('description', '').strip()

        cursor.execute("""
            INSERT INTO income (source, amount, date, description)
            VALUES (?, ?, ?, ?)
        """, (source, amount, date, description))
        conn.commit()
        flash('Income entry recorded successfully!', 'success')
        return redirect(url_for('income.manage_income'))

    # Retrieve all income records
    cursor.execute("SELECT * FROM income ORDER BY date DESC, id DESC")
    incomes = [dict(row) for row in cursor.fetchall()]

    # Stats
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income")
    total_income = cursor.fetchone()[0]

    current_month_str = datetime.now().strftime('%Y-%m')
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE strftime('%Y-%m', date) = ?", (current_month_str,))
    monthly_income = cursor.fetchone()[0]

    conn.close()
    today_str = datetime.now().strftime('%Y-%m-%d')

    return render_template(
        'income.html',
        incomes=incomes,
        total_income=total_income,
        monthly_income=monthly_income,
        today_str=today_str
    )

@income_bp.route('/income/delete/<int:income_id>', methods=['POST'])
def delete_income(income_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id = ?", (income_id,))
    conn.commit()
    conn.close()
    flash('Income entry deleted!', 'info')
    return redirect(url_for('income.manage_income'))
