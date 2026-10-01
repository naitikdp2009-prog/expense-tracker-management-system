from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database.database import get_db_connection, seed_demo_data

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings_view():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        currency = request.form.get('currency', '₹')
        theme = request.form.get('theme', 'dark')
        ai_provider = request.form.get('ai_provider', 'rule-based')

        cursor.execute("INSERT OR REPLACE INTO user_settings (key, value) VALUES ('currency', ?)", (currency,))
        cursor.execute("INSERT OR REPLACE INTO user_settings (key, value) VALUES ('theme', ?)", (theme,))
        cursor.execute("INSERT OR REPLACE INTO user_settings (key, value) VALUES ('ai_provider', ?)", (ai_provider,))
        
        conn.commit()
        conn.close()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings.settings_view'))

    cursor.execute("SELECT key, value FROM user_settings")
    settings_rows = cursor.fetchall()
    settings_dict = {row['key']: row['value'] for row in settings_rows}

    conn.close()
    return render_template('settings.html', settings=settings_dict)

@settings_bp.route('/api/settings/seed-data', methods=['POST'])
def api_seed_data():
    msg = seed_demo_data(force=True)
    return jsonify({'status': 'success', 'message': msg})

@settings_bp.route('/api/settings/get-currency')
def get_currency():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_settings WHERE key = 'currency'")
    row = cursor.fetchone()
    currency = row['value'] if row else '₹'
    conn.close()
    return jsonify({'currency': currency})
