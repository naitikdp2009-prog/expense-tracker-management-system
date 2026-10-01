from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from database.database import get_db_connection
from services.budget_alerts import evaluate_budget_alerts
from datetime import datetime
import csv
import io

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses')
def list_expenses():
    category_id = request.args.get('category_id', type=int)
    payment_method = request.args.get('payment_method', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'date_desc')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all categories for filter dropdown
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(row) for row in cursor.fetchall()]

    query = """
        SELECT e.id, e.amount, e.date, e.description, e.payment_method, e.notes,
               c.id as category_id, c.name as category_name, c.icon, c.color
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE 1=1
    """
    params = []

    if category_id:
        query += " AND e.category_id = ?"
        params.append(category_id)

    if payment_method:
        query += " AND e.payment_method = ?"
        params.append(payment_method)

    if start_date:
        query += " AND e.date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND e.date <= ?"
        params.append(end_date)

    if search_query:
        query += " AND (e.description LIKE ? OR e.notes LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Sorting
    if sort_by == 'date_asc':
        query += " ORDER BY e.date ASC, e.id ASC"
    elif sort_by == 'amount_desc':
        query += " ORDER BY e.amount DESC"
    elif sort_by == 'amount_asc':
        query += " ORDER BY e.amount ASC"
    else:
        query += " ORDER BY e.date DESC, e.id DESC"

    cursor.execute(query, params)
    expenses = [dict(row) for row in cursor.fetchall()]

    # Compute filtered total
    filtered_total = sum(e['amount'] for e in expenses)

    conn.close()

    return render_template(
        'expenses.html',
        expenses=expenses,
        categories=categories,
        filtered_total=filtered_total,
        selected_category=category_id,
        selected_payment=payment_method,
        start_date=start_date,
        end_date=end_date,
        search_query=search_query,
        sort_by=sort_by
    )

@expenses_bp.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        amount = float(request.form['amount'])
        category_id = int(request.form['category_id'])
        date = request.form['date']
        description = request.form['description'].strip()
        payment_method = request.form.get('payment_method', 'Cash')
        notes = request.form.get('notes', '').strip()

        cursor.execute("""
            INSERT INTO expenses (amount, category_id, date, description, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (amount, category_id, date, description, payment_method, notes))
        conn.commit()
        conn.close()

        # Trigger budget alert re-evaluation
        evaluate_budget_alerts()

        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses.list_expenses'))

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()

    today_str = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_expense.html', categories=categories, today_str=today_str)

@expenses_bp.route('/expenses/edit/<int:expense_id>', methods=['POST'])
def edit_expense(expense_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    amount = float(request.form['amount'])
    category_id = int(request.form['category_id'])
    date = request.form['date']
    description = request.form['description'].strip()
    payment_method = request.form.get('payment_method', 'Cash')
    notes = request.form.get('notes', '').strip()

    cursor.execute("""
        UPDATE expenses
        SET amount = ?, category_id = ?, date = ?, description = ?, payment_method = ?, notes = ?
        WHERE id = ?
    """, (amount, category_id, date, description, payment_method, notes, expense_id))
    conn.commit()
    conn.close()

    evaluate_budget_alerts()
    flash('Expense updated successfully!', 'success')
    return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    evaluate_budget_alerts()
    flash('Expense deleted successfully!', 'info')
    return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/expenses/export')
def export_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.date, c.name as category, e.description, e.amount, e.payment_method, e.notes
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Category', 'Description', 'Amount', 'Payment Method', 'Notes'])

    for row in rows:
        writer.writerow([row['id'], row['date'], row['category'], row['description'], row['amount'], row['payment_method'], row['notes']])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=expenses_export_{datetime.now().strftime("%Y%m%d")}.csv'
    return response
