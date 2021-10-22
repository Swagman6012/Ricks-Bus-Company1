from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'BusCompany'

mysql = MySQL(app)


# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE username = %s AND password = %s', (username, password,))

        customer = cursor.fetchone()

        if customer:

            session['loggedin'] = True
            session['id'] = customer['id']
            session['username'] = customer['username']

            return homepagetwo()
        else:

            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)


@app.route('/pythonlogin/homepage2')
def homepagetwo():
    if 'loggedin' in session:
        return render_template('homepagetwo.html')

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)

    return redirect(url_for('homepage'))


# http://localhost:5000/Falsk/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'phone' in request.form:

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Customer WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', phone):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', firstname):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', lastname):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not phone or not firstname or not lastname:
            msg = 'Please fill out the form!'
        else:

            cursor.execute('INSERT INTO customer VALUES (NULL, %s, %s, %s, %s, %s, %s)',
                           (firstname, lastname, username, password, email, phone))
            mysql.connection.commit()
            msg = 'You have successfully registered!'


    elif request.method == 'POST':

        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)


@app.route('/pythonlogin/profilepage')
def profilePage():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE id = %s', (session['id'],))
        customer = cursor.fetchone()
        return render_template('profilepage.html', customer=customer)

    return redirect(url_for('login'))


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/pythonlogin/reservationone', methods=['GET', 'POST'])
def reservation():
    msg = ''

    if request.method == 'POST' and 'date' in request.form and 'time' in request.form and 'droplocation' in request.form and 'picklocation' in request.form and 'miles' in request.form and 'passengeramount' in request.form:

        date = request.form['date']
        time = request.form['time']
        droplocation = request.form['droplocation']
        picklocation = request.form['picklocation']
        miles = request.form['miles']
        passengeramount = request.form['passengeramount']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ticket WHERE date = %s', (date,))
        account = cursor.fetchone()

        if account:
            msg = 'Reservation already exists!'
        elif not date or not time or not droplocation or not picklocation or not miles or not passengeramount:
            msg = 'Please fill out the form!'
        else:

            cursor.execute('INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, NULL, %s)',
                           (date, time, droplocation, picklocation, miles, passengeramount, session['id']))
            mysql.connection.commit()
            msg = 'You have successfully registered!'


    elif request.method == 'POST':

        msg = 'Please fill out the form!'

    return render_template('Reservation.html', msg=msg)


@app.route('/pythonlogin/viewticket', methods=["GET"])
def viewticket():
    x = 0
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ticket WHERE id = %s', (session['id'],))
        customer = cursor.fetchone()

        return render_template('viewticket.html', customer=customer)

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()