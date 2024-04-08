import sqlite3

# Database initialization
def init_db():
    conn = sqlite3.connect('expense_tracker.db')
    c = conn.cursor()

    # Create users table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT,username TEXT,firstname TEXT,lastname TEXT, password TEXT,confirmpassword TEXT)''')

    # Create expense table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS expense
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 amount DECIMAL(10, 2) NOT NULL,
                 category VARCHAR(50) NOT NULL,
                 description TEXT,
                 date DATE NOT NULL,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

# Call the function to initialize the database
init_db()
