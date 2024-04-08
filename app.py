from flask import Flask, render_template, request, redirect, url_for, session,make_response
import sqlite3
import database as db
import matplotlib.pyplot as plt
from io import BytesIO
import base64



app = Flask(__name__)
app.secret_key = 'your_secret_key'


db.init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (email,username,firstname,lastname,password,confirmpassword) VALUES (?, ?, ?, ?, ?, ?)", (email,username,firstname,lastname,password,confirmpassword))
        conn.commit()
        conn.close()
        
        return render_template('index.html')
    return render_template('signup.html')

@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date=request.form['date']
        
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        c.execute("INSERT INTO expense (amount, category,description,date) VALUES (?,?,?,?)", (amount, category,description,date))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('addexpense.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        response = make_response(render_template('dashboard.html', username=session['username']))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return redirect(url_for('login'))

@app.route('/predict_expense')
def predict_expense():
    # Plotting the future expenses predictions
    categories = ['Food', 'Transport', 'Shopping', 'Utilities']
    expenses = [400, 200, 250, 150]
    plt.figure(figsize=(6, 6))
    plt.bar(categories, expenses, color='salmon')
    plt.xlabel('Categories')
    plt.ylabel('Expenses')
    plt.title('Future Expenses Predictions')

    # Saving plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Converting bytes object to base64 encoded string
    plot_data = base64.b64encode(buffer.read()).decode()

    return render_template('prediction.html', plot_data=plot_data)

def fetch_actual_expenses():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    cur.execute("SELECT rowid, amount, category, date FROM expense")  # Include rowid for delete/edit actions
    expenses = cur.fetchall()
    conn.close()
    return expenses

def actual_expenses():
    #expenses_data = fetch_actual_expenses()

    #categories, expenses = zip(*expenses_data)

    categories = ['Food', 'Transport', 'Shopping', 'Utilities']
    expenses = [400, 200, 250, 150]
    plt.figure(figsize=(6, 6))
    plt.bar(categories, expenses, color='salmon')
    plt.xlabel('Categories')
    plt.ylabel('Expenses')
    plt.title('Actual Expenses Predictions')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plot_data_actual = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return render_template('prediction.html', plot_data=plot_data_actual)

@app.route('/viewexpense')
def show_expenses():
    expenses = fetch_actual_expenses()
    return render_template('viewexpense.html', expenses=expenses)

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if request.method == 'POST':
        # Process the form data and update the expense in the database
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        # Assume conn is your database connection and you've imported necessary modules
        conn.execute("UPDATE expense SET amount = ?, category = ?, date = ? WHERE rowid = ?", (amount, category, date, expense_id))
        conn.commit()
        return redirect(url_for('show_expenses'))
    else:
        conn = sqlite3.connect('expense_tracker.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cur = conn.cursor()
        cur.execute("SELECT rowid, amount, category, date FROM expense WHERE rowid = ?", (expense_id,))
        expense = cur.fetchone()
        conn.close()
        if expense:
            return render_template('edit_expense.html', expense=expense)
        else:
            return 'Expense not found', 404


@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    response = make_response(redirect(url_for('index')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run()
