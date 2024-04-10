from flask import Flask, render_template, request, redirect, url_for, session,make_response,flash
import sqlite3
import database as db
import matplotlib.pyplot as plt
from io import BytesIO
import base64



app = Flask(__name__)
app.secret_key = 'your_secret_key'

uname=''
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
        phone=request.form['tel']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
        # Username already exists, return an error message
            flash("Signup failed. Please try again.")
            return redirect(url_for('signup'))
        else:
            c.execute("INSERT INTO users (email,username,firstname,lastname,phone,password) VALUES (?, ?, ?, ?, ?, ?)", (email,username,firstname,lastname,phone,password))
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
        c.execute("INSERT INTO expense (userid,amount, category,description,date) VALUES (?,?,?,?,?)", (session['userid'],amount, category,description,date))
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
            session['userid']=user[0]
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
    #cur.execute("SELECT id, amount, category, date FROM expense")  # Include id for delete/edit actions
    cur.execute("SELECT  id,amount, category, date FROM expense WHERE userid = ?", (session['userid'],))
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
    conn = sqlite3.connect('expense_tracker.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM expense")
    categories = [row['category'] for row in cur.fetchall()]
    return render_template('viewexpense.html', expenses=expenses,categories=categories)



@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if request.method == 'POST':
        conn = sqlite3.connect('expense_tracker.db')
        # Process the form data and update the expense in the database
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        # Assume conn is your database connection and you've imported necessary modules
        conn.execute("UPDATE expense SET amount = ?, category = ?, date = ? WHERE id = ?", (amount, category, date,expense_id,))
        conn.commit()
        expenses = fetch_actual_expenses()
        return render_template('viewexpense.html', expenses=expenses)
    else:
        conn = sqlite3.connect('expense_tracker.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cur = conn.cursor()
        cur.execute("SELECT  id,amount, category, date FROM expense WHERE userid = ?", (session['userid'],))
        expense = cur.fetchone()
        conn.close()
        if expense:
            return render_template('editexpense.html', expense=expense)
        else:
            return 'Expense not found', 404
        

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    # Connect to the database
    conn = sqlite3.connect('expense_tracker.db')
    cur = conn.cursor()

    # Delete the expense with the given expense_id
    cur.execute("DELETE FROM expense WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    # Fetch the updated list of expenses or redirect to the main view
    # Assuming there's a function or route that shows all expenses
    expenses = fetch_actual_expenses()
    return render_template('viewexpense.html', expenses=expenses)


@app.route('/profile', methods=['GET','POST'])
def profile():
        if  request.method == "POST":
            email = request.form['email']
            username = request.form['username']
            firstname=request.form['firstname']
            lastname=request.form['lastname']
            phone=request.form['phone']
            password = request.form['password']
            conn = sqlite3.connect('expense_tracker.db')
            cur = conn.cursor()
            cur.execute("SELECT id, amount, category, date FROM expense")
            expenses = cur.fetchall()
            conn.close()
            print(expenses)
            return render_template('profile.html')
        else:
            print('get')
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
