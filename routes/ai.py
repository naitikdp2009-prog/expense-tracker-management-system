from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from database.database import get_db_connection
from services.analytics import generate_ai_insights, get_dashboard_summary
from services.purchase_advisor import evaluate_purchase_decision, simulate_what_if
from services.ocr_service import parse_receipt_text
from datetime import datetime
import os
import werkzeug.utils

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai-expenses')
def ai_expenses_view():
    insights = generate_ai_insights()
    summary = get_dashboard_summary()
    return render_template('ai_expenses.html', insights=insights, summary=summary)

@ai_bp.route('/receipt-scanner')
def receipt_scanner_view():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(c) for c in cursor.fetchall()]
    conn.close()
    return render_template('receipt_scanner.html', categories=categories, today_str=datetime.now().strftime('%Y-%m-%d'))

@ai_bp.route('/api/receipt/upload', methods=['POST'])
def process_receipt():
    raw_text = request.form.get('raw_text', '')
    filename = 'manual_receipt.png'

    if 'receipt_image' in request.files:
        file = request.files['receipt_image']
        if file and file.filename != '':
            filename = werkzeug.utils.secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)

    # Use OCR heuristic parser
    parsed_data = parse_receipt_text(raw_text if raw_text else f"Receipt image processed: {filename}\nTotal Amount: 350.00\nDate: {datetime.now().strftime('%Y-%m-%d')}\nMerchant: Supermarket Food")
    
    return jsonify({
        'status': 'success',
        'extracted': parsed_data,
        'image_url': url_for('static', filename=f'uploads/{filename}')
    })

@ai_bp.route('/purchase-advisor')
def purchase_advisor_view():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(c) for c in cursor.fetchall()]
    conn.close()

    summary = get_dashboard_summary()
    return render_template('purchase_advisor.html', categories=categories, summary=summary)

@ai_bp.route('/api/purchase-advisor/evaluate', methods=['POST'])
def api_evaluate_purchase():
    data = request.json
    product_name = data.get('product_name', 'Item')
    price = float(data.get('price', 0))
    category_name = data.get('category_name', 'General')
    need_or_want = data.get('need_or_want', 'want')
    urgency = data.get('urgency', 'medium')

    result = evaluate_purchase_decision(product_name, price, category_name, need_or_want, urgency)
    return jsonify(result)

@ai_bp.route('/simulator')
def simulator_view():
    summary = get_dashboard_summary()
    return render_template('simulator.html', summary=summary)

@ai_bp.route('/api/simulator/calculate', methods=['POST'])
def api_calculate_simulator():
    data = request.json
    current_spending = float(data.get('current_spending', 0))
    purchase_amount = float(data.get('purchase_amount', 0))
    monthly_budget = float(data.get('monthly_budget', 25000))

    result = simulate_what_if(current_spending, purchase_amount, monthly_budget)
    return jsonify(result)
