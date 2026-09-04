import sqlite3
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Database Setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Create a data directory if it doesn't exist (Crucial for Docker)
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, 'budget.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # 1. Existing Tracker Tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            archived INTEGER DEFAULT 0
        )
    ''')
    try:
        conn.execute('ALTER TABLE transactions ADD COLUMN archived INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass 
        
    conn.execute('''
        CREATE TABLE IF NOT EXISTS monthly_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            close_date TEXT NOT NULL,
            utilities_spent REAL,
            debt_spent REAL,
            living_spent REAL,
            misc_spent REAL
        )
    ''')
    
    # 2. NEW Configuration Table for Dynamic Sliders
    conn.execute('''
        CREATE TABLE IF NOT EXISTS config_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,       -- 'income', 'investment', or 'budget'
            category TEXT,            -- e.g., 'housing', 'debt', 'living' (only used if type='budget')
            item_id TEXT NOT NULL,    -- internal HTML id
            label TEXT NOT NULL,      -- Display name
            amount REAL NOT NULL,     -- Default slider value
            max_amount REAL NOT NULL, -- Max slider value
            is_biweekly INTEGER DEFAULT 0 -- For calculating Optomi or other biweekly checks
        )
    ''')
    
    # 3. Seed Database if Configuration is Empty
    if not conn.execute('SELECT 1 FROM config_items LIMIT 1').fetchone():
        seed_data = [
            # Income
            ('income', '', 'pension', 'Pension', 2943.35, 4000, 0),
            ('income', '', 'va_disability', 'VA Disability', 2698.02, 5000, 0),
            ('income', '', 'optomi_paycheck', 'Optomi Paycheck', 3359.14, 4000, 1),
            # Investments
            ('investment', '', 'investment_1', 'Investment', 600, 1000, 0),
            # Housing & Utilities
            ('budget', 'housing', 'mortgage', 'Mortgage', 1267, 2500, 0),
            ('budget', 'housing', 'utilities', 'Electric & Water', 750, 1500, 0),
            ('budget', 'housing', 'comms', 'Phone & Internet', 408, 800, 0),
            ('budget', 'housing', 'insurance', 'Home/Auto Insurance', 347, 800, 0),
            ('budget', 'housing', 'life_ins', 'Life Insurance', 106, 300, 0),
            # Family
            ('budget', 'family', 'college', "Hannah's College Transfer", 900, 2000, 0),
            # Debt
            ('budget', 'debt', 'auto', 'Auto Loans', 1419, 2500, 0),
            ('budget', 'debt', 'bnpl', 'Affirm', 664, 1000, 0),
            ('budget', 'debt', 'Microf', 'Microf', 501, 600, 0),
            ('budget', 'debt', 'upstart', 'Upstart', 70, 100, 0),
            ('budget', 'debt', 'cc', 'Credit Cards', 392, 1000, 0),
            ('budget', 'debt', 'regional', 'Regional Finance', 299, 800, 0),
            ('budget', 'debt', 'spectrum', 'Spectrum Payoff', 218, 500, 0),
            # Living
            ('budget', 'living', 'groceries', 'Groceries', 600, 1500, 0),
            ('budget', 'living', 'misc_shop', 'Household & Misc', 350, 1000, 0),
            ('budget', 'living', 'dining', 'Dining Out', 300, 1000, 0),
            ('budget', 'living', 'gas', 'Gas & Auto Fuel', 250, 800, 0),
            # Subs
            ('budget', 'subs', 'hulu', 'Hulu', 100, 200, 0),
            ('budget', 'subs', 'streaming', 'Streaming Services', 86, 200, 0),
            ('budget', 'subs', 'cloud', 'Cloud & Subscriptions', 87, 200, 0)
        ]
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO config_items (type, category, item_id, label, amount, max_amount, is_biweekly)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_data)
        conn.commit()
        
    conn.close()

init_db()

# --- Routes ---

@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM config_items').fetchall()
    conn.close()

    income_data = []
    investment_data = []
    
    # Base structure for the dashboard categories
    budget_dict = {
        'housing': {"id": "housing", "title": "Housing & Utilities", "color": "#1a73e8", "items": []},
        'family': {"id": "family", "title": "Family Obligations", "color": "#9c27b0", "items": []},
        'debt': {"id": "debt", "title": "Debt Minimums", "color": "#d93025", "items": []},
        'living': {"id": "living", "title": "Daily Living", "color": "#34a853", "items": []},
        'subs': {"id": "subs", "title": "Subscriptions", "color": "#f29900", "items": []}
    }

    # Sort database items into the correct HTML structures
    for row in items:
        obj = {
            'id': row['item_id'],
            'label': row['label'],
            'value': row['amount'],
            'max': row['max_amount'],
            'is_biweekly': row['is_biweekly']
        }
        
        if row['type'] == 'income':
            income_data.append(obj)
        elif row['type'] == 'investment':
            investment_data.append(obj)
        elif row['type'] == 'budget':
            cat = row['category']
            if cat in budget_dict:
                budget_dict[cat]['items'].append(obj)

    # Only pass categories that actually contain items
    budget_data = [v for k, v in budget_dict.items() if len(v['items']) > 0]

    return render_template('index.html', income_data=income_data, investment_data=investment_data, budget_data=budget_data)

@app.route('/settings')
def settings():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM config_items ORDER BY type, category').fetchall()
    conn.close()
    
    # Convert to dictionaries for easier Jinja parsing
    config_list = [dict(row) for row in items]
    return render_template('settings.html', items=config_list)

@app.route('/api/add_config', methods=['POST'])
def add_config():
    data = request.get_json()
    # Generate a unique HTML ID for the new slider
    item_id = 'item_' + uuid.uuid4().hex[:8] 
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO config_items (type, category, item_id, label, amount, max_amount, is_biweekly)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['type'], 
        data.get('category', ''), 
        item_id, 
        data['label'], 
        float(data['amount']), 
        float(data['max_amount']), 
        int(data.get('is_biweekly', 0))
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/delete_config/<int:item_id>', methods=['DELETE'])
def delete_config(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM config_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/tracker')
def tracker():
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions WHERE archived = 0').fetchall()
    
    # Dynamically calculate the tracker targets based on the current configuration
    config_items = conn.execute("SELECT * FROM config_items WHERE type = 'budget'").fetchall()
    conn.close()
    
    tracker_targets = {'utilities': 0, 'debt': 0, 'living': 0, 'misc': 0}
    for row in config_items:
        if row['category'] in ['housing', 'subs']:
            tracker_targets['utilities'] += row['amount']
        elif row['category'] == 'debt':
            tracker_targets['debt'] += row['amount']
        elif row['category'] == 'living':
            tracker_targets['living'] += row['amount']
        else: # Family or any future custom categories
            tracker_targets['misc'] += row['amount']
            
    data = {'utilities': [], 'debt': [], 'living': [], 'misc': []}
    for row in transactions:
        cat = row['category']
        if cat in data:
            data[cat].append({
                'id': row['id'], 'date': row['date'], 
                'description': row['description'], 'amount': row['amount']
            })
            
    return render_template('budget_tracker.html', existing_data=data, tracker_targets=tracker_targets)

# [KEEP YOUR EXISTING /add_transaction and /close_month ROUTES HERE EXACTLY AS THEY WERE]
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    req_data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO transactions (category, date, description, amount) VALUES (?, ?, ?, ?)',
                   (req_data['category'], req_data['date'], req_data['description'], float(req_data['amount'])))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return jsonify({'status': 'success', 'id': inserted_id})

@app.route('/close_month', methods=['POST'])
def close_month():
    conn = get_db_connection()
    cursor = conn.execute('SELECT category, SUM(amount) as total FROM transactions WHERE archived = 0 GROUP BY category')
    totals = {row['category']: row['total'] for row in cursor}
    conn.execute('''
        INSERT INTO monthly_summary (close_date, utilities_spent, debt_spent, living_spent, misc_spent)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), totals.get('utilities', 0), totals.get('debt', 0), totals.get('living', 0), totals.get('misc', 0)))
    conn.execute('UPDATE transactions SET archived = 1 WHERE archived = 0')
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)