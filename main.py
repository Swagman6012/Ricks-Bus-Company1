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
            if customer is None:
                session['numtickets'] = 0
                session['currentticket'] = 0
            else:
                session['numtickets'] = customer['numtickets']
                session['currentticket'] = customer['numtickets']

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

            cursor.execute('INSERT INTO customer VALUES (NULL, %s, %s, %s, %s, %s, %s, 0)',
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


@app.route('/pythonlogin/adminprofilepage')
def adminprofilepage():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['id'],))
        Admin = cursor.fetchone()
        return render_template('adminprofilepage.html', Admin=Admin)

    return redirect(url_for('login'))


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/pythonlogin/reservation', methods=['GET', 'POST'])
def reservation():
    def price(m, passengera):
        price = int(m) // 10
        price *= 5
        price *= int(passengera)
        return int(price)

    msg = ''

    if request.method == 'POST' and 'date' in request.form and 'time' in request.form and 'droplocation' in request.form and 'picklocation' in request.form and 'miles' in request.form and 'passengeramount' in request.form:

        date = request.form['date']
        time = request.form['time']
        droplocation = request.form['droplocation']
        picklocation = request.form['picklocation']
        miles = request.form['miles']
        passengeramount = request.form['passengeramount']
        balance = price(miles, passengeramount)
        price = balance

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ticket WHERE date = %s and time = %s', (date, time))
        account = cursor.fetchone()

        if account:
            msg = 'Reservation already exists!'

        elif not date or not time or not droplocation or not picklocation or not miles or not passengeramount:
            msg = 'Please fill out the form!'
        else:

            session['numtickets'] = session['numtickets'] + 1
            session['currentticket'] = session['numtickets']
            cursor.execute('INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, NULL)',
                           (date, time, droplocation, picklocation, miles, passengeramount, price, balance,
                            session['id'], session['numtickets']))
            cursor.execute('UPDATE customer SET numtickets = %s WHERE id = %s', (session['numtickets'], session['id']))
            mysql.connection.commit()
            msg = 'You have successfully reserved a trip!'


    elif request.method == 'POST':

        msg = 'Please fill out the form!'

    return render_template('Reservation.html', msg=msg)

@app.route('/pythonlogin/adminviewticket/editticket', methods=['GET', 'POST'])
def editticket():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM ticket WHERE ticket_id = %s', (session['ticketid']+1,))
    customer = cursor.fetchone()

    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ticket WHERE ticket_id = %s', (session['ticketid'] + 1,))
        account = cursor.fetchone()
        balance = request.form['balance']
        price = request.form['price']
        if balance == '':
            balance = account['balance']
        if price == '':
            price = account['price']

        cursor.execute('UPDATE ticket SET price = %s, balance = %s where ticket_id =%s ', (price, balance, session['ticketid']+1))
        mysql.connection.commit()
        return render_template('editticket.html', customer=customer)

    return render_template('editticket.html', customer=customer)

@app.route('/pythonlogin/profilepage/editprofile', methods=['GET', 'POST'])
def editprofile():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Customer WHERE id = %s', (session['id'],))
    customer = cursor.fetchone()


    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Customer WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        if firstname == '':
            firstname = account['firstname']
        if lastname == '':
            lastname = account['lastname']

        if password =='':
            password = account['password']

        if email == '':
            email = account['email']

        if phone == '':
            phone = account['phone']


        cursor.execute('UPDATE Customer SET firstname = %s, lastname = %s, password = %s, email = %s, phone = %s where id = %s ', (firstname, lastname, password, email, phone, session['id']))
        mysql.connection.commit()
        return render_template('editprofile.html', customer=customer)


    return render_template('editprofile.html', customer=customer)
@app.route('/adminregister', methods=['GET', 'POST'])
def adminregister():
    msg = ''

    if request.method == 'POST' and 'adminfirstname' in request.form and 'adminlastname' in request.form and 'adminusername' in request.form and 'adminpassword' in request.form and 'adminemail' in request.form and 'adminphone' in request.form and 'employercode' in request.form:

        firstname = request.form['adminfirstname']
        lastname = request.form['adminlastname']
        username = request.form['adminusername']
        password = request.form['adminpassword']
        email = request.form['adminemail']
        phone = request.form['adminphone']
        employercode = request.form['employercode']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Admin WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', phone):
            msg = 'phone must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', firstname):
            msg = 'firstname must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', lastname):
            msg = 'Lastname must contain only characters!'
        elif not username or not password or not email or not phone or not firstname or not lastname or not employercode:
            msg = 'Please fill out the form!'
        else:

            cursor.execute('INSERT INTO Admin VALUES (NULL, %s, %s, %s, %s, %s, %s )',
                           (firstname, lastname, username, password, email, phone))
            mysql.connection.commit()
            msg = 'You have successfully registered as an Admin!'

    elif request.method == 'POST':

        msg = 'Please fill out the form!'

    return render_template('adminregister.html', msg=msg)


@app.route('/pythonlogin/adminhomepage')
def homepageadmin():
    if 'loggedin' in session:
        return render_template('Adminhomepage.html')

    return redirect(url_for('adminlogin'))


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    msg = ''

    if request.method == 'POST' and 'adminusername' in request.form and 'adminpassword' in request.form and 'employercode':

        username = request.form['adminusername']
        password = request.form['adminpassword']
        employercode = request.form['employercode']
        if employercode != '123456':
            return render_template('adminlogin.html')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Admin WHERE username = %s AND password = %s', (username, password,))

        admin = cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from ticket ORDER by ticket_id DESC LIMIT 1')
        ticket = cursor.fetchone()

        if admin:

            session['loggedin'] = True
            session['id'] = admin['admin_id']
            session['username'] = admin['username']
            if ticket is not None:

                session['ticketid'] = ticket['ticket_id']
                session['numtickets'] = ticket['ticket_id']
            else:
                session['ticketid'] = 0
                session['numtickets'] = 0
            return homepageadmin()
        else:

            msg = 'Incorrect username/password!'

    return render_template('adminlogin.html', msg=msg)


@app.route('/pythonlogin/viewticket', methods=["GET"])
def viewticket():
    x = 0
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ticket WHERE id = %s AND custicketid = %s',
                       (session['id'], session['currentticket']))
        customer = cursor.fetchone()
        session['currentticket'] = session['currentticket'] - 1
        if session['currentticket'] == 0:
            session['currentticket'] = session['numtickets']

        return render_template('viewticket.html', customer=customer)

    return redirect(url_for('login'))


@app.route('/pythonlogin/adminviewticket', methods=['GET','POST'])
def adminviewticket():
    x = 0
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ticket  where ticket_id = %s ', (session['ticketid'],))
        customer = cursor.fetchone()
        if request.method == "POST":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM ticket where ticket_id = %s', (session['ticketid']+1,))
            mysql.connection.commit()
        session['ticketid'] = session['ticketid'] - 1
        if session['ticketid'] == 0:
            session['ticketid'] = session['numtickets']



        return render_template('adminviewticket.html', customer=customer)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
