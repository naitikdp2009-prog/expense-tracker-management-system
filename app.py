from flask import Flask, render_template, jsonify
from config import Config
from database.database import init_db, seed_demo_data, get_db_connection
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize Database & Seed Demo Data
    with app.app_context():
        init_db()
        seed_demo_data(force=False)

    # Register Blueprints
    from routes.main import main_bp
    from routes.dashboard import dashboard_bp
    from routes.expenses import expenses_bp
    from routes.income import income_bp
    from routes.budget import budget_bp
    from routes.reports import reports_bp
    from routes.ai import ai_bp
    from routes.chat import chat_bp
    from routes.settings import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(settings_bp)

    @app.context_processor
    def inject_global_vars():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM user_settings WHERE key = 'currency'")
        r_curr = cursor.fetchone()
        currency = r_curr['value'] if r_curr else '₹'

        cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
        unread_alerts_count = cursor.fetchone()[0]

        cursor.execute("SELECT value FROM user_settings WHERE key = 'theme'")
        r_theme = cursor.fetchone()
        theme = r_theme['value'] if r_theme else 'dark'

        conn.close()
        return dict(currency_symbol=currency, unread_alerts_count=unread_alerts_count, active_theme=theme)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('about.html'), 404

    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print(" EXPENSE TRACKER MANAGEMENT SYSTEM")
    print(" College Minor Project Review-2 Version")
    print(" Local Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
