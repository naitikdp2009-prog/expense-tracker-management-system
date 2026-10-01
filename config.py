import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'college-minor-project-review2-secret-key-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, 'expense_tracker.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Optional External AI API integration settings
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'rule-based') # 'rule-based', 'openai', 'gemini'
