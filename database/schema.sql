-- Database Schema for Expense Tracker Management System

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT NOT NULL DEFAULT 'fa-tags',
    color TEXT NOT NULL DEFAULT '#6366f1'
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    payment_method TEXT NOT NULL DEFAULT 'Cash',
    notes TEXT,
    receipt_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER, -- NULL indicates Overall Monthly Budget
    monthly_limit REAL NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, month, year),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info', -- 'info', 'warning', 'danger', 'success'
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant TEXT,
    amount REAL,
    date TEXT,
    category_id INTEGER,
    description TEXT,
    image_path TEXT NOT NULL,
    raw_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Pre-populate default categories
INSERT OR IGNORE INTO categories (id, name, icon, color) VALUES
(1, 'Food', 'fa-utensils', '#ef4444'),
(2, 'Transport', 'fa-bus', '#f59e0b'),
(3, 'Shopping', 'fa-shopping-bag', '#ec4899'),
(4, 'Education', 'fa-graduation-cap', '#3b82f6'),
(5, 'Entertainment', 'fa-film', '#8b5cf6'),
(6, 'Bills', 'fa-file-invoice-dollar', '#10b981'),
(7, 'Healthcare', 'fa-heartbeat', '#06b6d4'),
(8, 'Travel', 'fa-plane', '#14b8a6'),
(9, 'Other', 'fa-ellipsis-h', '#6b7280');

-- Pre-populate default settings
INSERT OR IGNORE INTO user_settings (key, value) VALUES
('currency', '₹'),
('theme', 'dark'),
('ai_provider', 'rule-based');
