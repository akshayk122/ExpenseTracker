import calendar
from flask import Flask, render_template, request, redirect, url_for, session,make_response,flash,jsonify
import sqlite3
import database as db
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import Flask, request, render_template
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Path\To\Tesseract-OCR\tesseract.exe'  # Update this path
import re
from datetime import datetime
import numpy as np
import scan_receipt as sn
from werkzeug.utils import secure_filename
import tempfile
import os
import time
from contextlib import contextmanager
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA



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
        role='user'
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
        # Username already exists, return an error message
            flash("Signup failed. Please try again.")
            return redirect(url_for('signup'))
        else:
            c.execute("INSERT INTO users (email,username,firstname,lastname,phone,password,role) VALUES (?, ?, ?, ?, ?, ?, ?)", (email,username,firstname,lastname,phone,password,role))
            conn.commit()
            conn.close()
        
        return render_template('index.html')
    return render_template('signup.html')


@app.route('/addadmin', methods=['GET', 'POST'])
def addadmin():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        phone=request.form['tel']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        role='admin'
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
        # Username already exists, return an error message
            flash("Signup failed. Please try again.")
            return redirect(url_for('addadmin'))
        else:
            c.execute("INSERT INTO users (email,username,firstname,lastname,phone,password,role) VALUES (?, ?, ?, ?, ?, ?, ?)", (email,username,firstname,lastname,phone,password,role))
            conn.commit()
            conn.close()
        return render_template('admindashboard.html')
    return render_template('addadmin.html')

@contextmanager
def temporary_file(suffix=''):
    """Create and yield a temporary file, ensuring its deletion afterward."""
    fd, temp_file_path = tempfile.mkstemp(suffix=suffix)
    try:
        yield temp_file_path
    finally:
        os.close(fd)
        os.unlink(temp_file_path)

@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date=request.form['date']
        file = request.files['bill']
        #file processing block
        if file.filename == '':
            return 'No selected file'
        if file:
            with temporary_file(suffix=os.path.splitext(file.filename)[1]) as temp_file_path:
                file.save(temp_file_path)
                data=sn.scan_image(temp_file_path)
                #print(data)
                
        #file processing end
        #data=sn.scan_image(file)
       
        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        c.execute("INSERT INTO expense (userid,amount, category,description,date) VALUES (?,?,?,?,?)", (session['userid'],amount, category,description,date))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('addexpense.html')

@app.route('/read_expense', methods=['GET', 'POST'])
def read_expense():
    if request.method == 'POST':
        print('post')
        file = request.files['bill']
        #file processing block
        if file.filename == '':
            return 'No selected file'
        if file:
            with temporary_file(suffix=os.path.splitext(file.filename)[1]) as temp_file_path:
                file.save(temp_file_path)
                data=sn.scan_image(temp_file_path)
                print(data)
    return data

@app.route('/read_bill', methods=['POST'])
def read_bill():
    print('read_bill')
    file = request.files['bill']
    print(file)
    if file.filename == '':
            return 'No selected file'
    if file:
            with temporary_file(suffix=os.path.splitext(file.filename)[1]) as temp_file_path:
                file.save(temp_file_path)
                total,category,data=sn.scan_image(temp_file_path)
                print(total,category)
    # Sample data you might want to return
    sample_data = {
        "status": "success",
        "message": "Data retrieved successfully",
        "data": {
            "id": 1,
            "description": "Sample item",
            "amount": 99.99,
            "date": "2024-04-17"
        }
    }
    sdata=data
    return jsonify(sdata)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def process_extracted_text(text):
    # Define a regular expression pattern to match the total amount
    # This pattern assumes the total amount is preceded by "Total" and followed by a number
    # You may need to adjust this pattern based on the format of your bills/receipts
    pattern = r'Total:?\s*\$?(\d+\.\d{2})'

    # Search for the pattern in the extracted text
    match = re.search(pattern, text, re.IGNORECASE)

    # If a match is found, return the total amount
    if match:
        return match.group(1)
    else:
        return None  # No total amount found

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        isactive='1'

        conn = sqlite3.connect('expense_tracker.db')
        c = conn.cursor()
        
        if role == 'admin':
            #redirect admin dashboard
            c.execute("SELECT * FROM users WHERE username = ? AND password = ? and role = ? AND isactive= ? ", (username, password,role,isactive))
            adminuser = c.fetchone()
            #print(adminuser)
            if adminuser:
                #print(user)
                session['username'] = adminuser[3]
                session['userid']=adminuser[0]
                return redirect(url_for('admindashboard'))
            else:
                return render_template('login.html', error='Invalid username or password')
        elif role == 'user':
            #redirect user dashboard
            c.execute("SELECT * FROM users WHERE username = ? AND password = ? and role = ? AND isactive= ? ", (username, password,role,isactive))
            user = c.fetchone()
            if user:
                #print(user)
                session['username'] = user[3]
                session['userid']=user[0]
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid username or password')
        else:
            #check if user exists in database
            print('no role')

        conn.close()
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        #read database data
        totalexpense=fetch_total_expenses()
        monthexpense,topcategory,topamount=fetch_currentmonth_expenses()
        actual=actual_expense_graph()
        monthlyexpsense=monthly_expense_graph()
        budgetdata=fetch_budget_data()
        month_num=budgetdata[1]
        month_name = calendar.month_name[month_num]
        #print(budgetdata)
        #print(totalexpense)
        response = make_response(render_template('dashboard.html', username=session['username'],totalexpense=totalexpense,monthexpense=monthexpense,actual=actual,monthlyexpsense=monthlyexpsense,topcategory=topcategory,topamount=topamount,budgetdata=budgetdata[3],month_name=month_name))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return redirect(url_for('login'))

#Admin dashboard
@app.route('/admindashboard', methods=['GET', 'POST'])
def admindashboard():
    if 'username' in session:
        #read database data
        conn = sqlite3.connect('expense_tracker.db')  
        cur = conn.cursor()
        #cur.execute("SELECT id, amount, category, date FROM expense")  # Include id for delete/edit actions
        cur.execute("SELECT  id,username,role FROM users")
        users = cur.fetchall()
        conn.close()
        #print(totalexpense)
        response = make_response(render_template('admindashboard.html', username=session['username'],users=users))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return redirect(url_for('login'))

@app.route('/predict_expense')
def predict_expense():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    # Plotting the future expenses predictions
    categories = ['food', 'transport', 'shopping', 'utilities']
    expenses = []
    for category in categories:
        cur.execute("SELECT SUM(amount) FROM expense WHERE userid = ? AND category = ?", (session['userid'], category))
        result = cur.fetchone()
        expense_amount = result[0] if result[0] is not None else 0
        expenses.append(expense_amount)

    #print(expenses)
    
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

@app.route('/predict_future_expense')
def predict_and_plot_expenses():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    categories = ['food', 'transport', 'shopping', 'utilities']
    predictions = []

    for category in categories:
        cur.execute("SELECT amount, date FROM expense WHERE userid = ? AND category = ?", (session['userid'], category))
        data = cur.fetchall()

        if not data:
            predictions.append(0)
            continue

        df = pd.DataFrame(data, columns=['amount', 'date'])
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)
        df['month_index'] = range(len(df))

        model = LinearRegression()
        X = df[['month_index']]
        y = df['amount']
        model.fit(X, y)

        next_month_index = df['month_index'].max() + 1
        predicted_expense = model.predict([[next_month_index]])
        predictions.append(predicted_expense[0])

    conn.close()

    # Plotting the predicted expenses
    plt.figure(figsize=(6, 6))
    plt.bar(categories, predictions, color='salmon')
    plt.xlabel('Categories')
    plt.ylabel('Expenses')
    plt.title('Future Expenses ')

    # Saving plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()  # Ensure to close the plot to free up memory
    buffer.seek(0)

    # Converting bytes object to base64 encoded string
    plot_data = base64.b64encode(buffer.read()).decode()

    return render_template('prediction.html', plot_data=plot_data)


def fetch_budget_data():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    #cur.execute("SELECT id, amount, category, date FROM expense")  # Include id for delete/edit actions
    current_date = datetime.now()
    month = current_date.month
    year = current_date.year
    cur.execute("SELECT   user_id, month, year, budget_amount  FROM budget WHERE user_id = ? AND month = ? AND year = ?", (session['userid'],month,year,))
    budget = cur.fetchone()
    conn.close()
    return budget

def fetch_actual_expenses():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    #cur.execute("SELECT id, amount, category, date FROM expense")  # Include id for delete/edit actions
    cur.execute("SELECT  id,amount, category, date FROM expense WHERE userid = ?", (session['userid'],))
    expenses = cur.fetchall()
    conn.close()
    return expenses

def fetch_total_expenses():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    #cur.execute("SELECT id, amount, category, date FROM expense")  # Include id for delete/edit actions
    cur.execute("SELECT  sum(amount) FROM expense WHERE userid = ?", (session['userid'],))
    mexpenses = cur.fetchone()
    total_expenses = mexpenses[0]
    conn.close()
    return total_expenses

def fetch_currentmonth_expenses():
    conn = sqlite3.connect('expense_tracker.db')
    cur = conn.cursor()

    # Get the current month and year as strings
    current_month = datetime.now().strftime('%m')
    current_year = datetime.now().strftime('%Y')

    # Query to sum the amount for the current month and year for the logged-in user
    cur.execute("SELECT SUM(amount) FROM expense WHERE userid = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?",
                (session['userid'], current_year, current_month))

    mexpenses = cur.fetchone()
    month_expenses = mexpenses[0] if mexpenses[0] is not None else 0  # Set to 0 if no expenses

    #top expense
    cur.execute("SELECT category, SUM(amount) as total FROM expense WHERE userid = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ? GROUP BY category ORDER BY total DESC LIMIT 1",
                (session['userid'], current_year, current_month))

    top_category = cur.fetchone()
    top_category_expense = top_category[1] if top_category else 0
    top_category_name = top_category[0] if top_category else "No expenses"

    conn.close()
    return month_expenses,top_category_expense,top_category_name


def actual_expense_graph():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    # Plotting the future expenses predictions
    categories = ['food', 'transport', 'shopping', 'utilities']
    expenses = []
    for category in categories:
        cur.execute("SELECT SUM(amount) FROM expense WHERE userid = ? AND category = ?", (session['userid'], category))
        result = cur.fetchone()
        expense_amount = result[0] if result[0] is not None else 0
        expenses.append(expense_amount)
    
    expenses = [expense if not np.isnan(expense) else 0 for expense in expenses]
   # Check if sum of expenses is zero
    if sum(expenses) == 0:
        # Handle the case where there are no expenses
        plt.figure(figsize=(4, 4))
        plt.pie([1], labels=[''], colors=['#cccccc'])
        plt.title('Actual Expenses')
    else:
        plt.figure(figsize=(4, 4))
        plt.pie(expenses, labels=categories, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
        plt.title('Actual Expenses')
    # Saving plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Converting bytes object to base64 encoded string
    actual_plot_data = base64.b64encode(buffer.read()).decode()
    return actual_plot_data

def monthly_expense_graph():
    conn = sqlite3.connect('expense_tracker.db')  
    cur = conn.cursor()
    # Plotting the future expenses predictions
    categories = ['food', 'transport', 'shopping', 'utilities']
    expenses = []
    # Get the current month and year as strings
    current_month = datetime.now().strftime('%m')
    current_year = datetime.now().strftime('%Y')
    for category in categories:
        cur.execute("SELECT SUM(amount) FROM expense WHERE userid = ? AND category = ?", (session['userid'], category))
        cur.execute("SELECT SUM(amount) FROM expense WHERE userid = ? AND category = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?",
                (session['userid'],category, current_year, current_month))
        result = cur.fetchone()
        expense_amount = result[0] if result[0] is not None else 0
        expenses.append(expense_amount)

    # Check if sum of expenses is zero
    if sum(expenses) == 0:
        # Handle the case where there are no expenses
        plt.figure(figsize=(4, 4))
        plt.pie([1], labels=[''], colors=['#cccccc'])
        plt.title('Actual Expenses')
    else:
        plt.figure(figsize=(4, 4))
        #plt.pie(expenses, labels=categories, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
        plt.title('Actual Monthly Expenses')
        plt.pie(expenses, labels=categories, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'], wedgeprops={'width': 0.3})


    # Saving plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Converting bytes object to base64 encoded string
    actual_mplot_data = base64.b64encode(buffer.read()).decode()
    return actual_mplot_data

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
        conn.close() 
        #return render_template('viewexpense.html', expenses=expenses)
        return redirect(url_for('dashboard'))
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
   

@app.route('/delete/<int:expense_id>', methods=['GET','POST'])
def delete_expense(expense_id):
    # Connect to the database
    conn = sqlite3.connect('expense_tracker.db')
    cur = conn.cursor()
    # Delete the expense with the given expense_id
    cur.execute("DELETE FROM expense WHERE id = ?",(expense_id,))
    conn.commit()
    conn.close()
    # Fetch the updated list of expenses or redirect to the main view
    # Assuming there's a function or route that shows all expenses
    cur.execute("SELECT DISTINCT category FROM expense")
    categories = [row['category'] for row in cur.fetchall()]
    expenses = fetch_actual_expenses()
    #return render_template('viewexpense.html', expenses=expenses,categories=categories)
    return redirect(url_for('viewexpense'))

@app.route('/edituser/<int:userid>', methods=['GET', 'POST'])
def edituser(userid):
    if request.method == 'POST':
        conn = sqlite3.connect('expense_tracker.db')
        # Process the form data and update the expense in the database
        user_id=request.form['id']
        activeflag = request.form['status']
        #print(user_id)
        # Assume conn is your database connection and you've imported necessary modules
        conn.execute("UPDATE users SET isactive = ? WHERE id = ?", (activeflag,user_id,))
        print('test11')
        conn.commit()
        expenses = fetch_actual_expenses()
        conn.close() 
        #return render_template('viewexpense.html', expenses=expenses)
        return redirect(url_for('admindashboard'))
    else:
        conn = sqlite3.connect('expense_tracker.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cur = conn.cursor()
        cur.execute("SELECT  id,isactive FROM users where id= ?",(userid,))
        userdata = cur.fetchone()
        conn.close() 
        if userdata:
            return render_template('edituser.html', userdata=userdata)
        else:
            return 'Expense not found', 404
        

@app.route('/deleteuser/<int:userid>', methods=['GET', 'POST'])
def deleteuser(userid):
    if request.method != 'POST':
        print('delete user in post')
        conn = sqlite3.connect('expense_tracker.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM users where id= ?",(userid,))
        print('Delete')
        conn.commit()
        conn.close() 
        #return render_template('viewexpense.html', expenses=expenses)
        return redirect(url_for('admindashboard'))
    else:
         return redirect(url_for('admindashboard'))


@app.route('/budgetupdate',methods=['GET', 'POST'])
def budgetupdate():
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    new_budget = request.form['totalBudget']
    current_date = datetime.now()
    month = current_date.month
    year = current_date.year
    sql = '''
    INSERT INTO budget (user_id, month, year, budget_amount)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id, month, year) DO UPDATE SET
    budget_amount = excluded.budget_amount
    WHERE user_id = ? AND month = ? AND year = ?
    '''
    cursor.execute(sql, (session['userid'], month, year, new_budget, session['userid'], month, year))
    print('budget')
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

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
            conn.execute("UPDATE users SET email = ?, username = ?, firstname = ?,lastname = ?,phone = ?,password = ? WHERE id = ?", (email, username, firstname,lastname,phone,password,session['userid'],))
            conn.commit()
            conn.close() 
            return redirect(url_for('dashboard'))
            #return render_template('profile.html')
        else:
            return render_template('profile.html')
        

@app.route('/adminprofile', methods=['GET','POST'])
def adminprofile():
        if  request.method == "POST":
            email = request.form['email']
            username = request.form['username']
            firstname=request.form['firstname']
            lastname=request.form['lastname']
            phone=request.form['phone']
            password = request.form['password']
            conn = sqlite3.connect('expense_tracker.db')
            #print(session['userid'])
            cur = conn.cursor()
            conn.execute("UPDATE users SET email = ?, username = ?, firstname = ?,lastname = ?,phone = ?,password = ? WHERE id = ?", (email, username, firstname,lastname,phone,password,session['userid'],))
            conn.commit()
            conn.close() 
            return redirect(url_for('admindashboard'))
        else:
            return render_template('adminprofile.html')

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
    app.run(debug=True)
