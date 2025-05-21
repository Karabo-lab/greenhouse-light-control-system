from flask import Flask, render_template, request, redirect, url_for, session,jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = '4431'  # Add a secret key for session management

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="karabo@2021",
    database="lightControlSys"
)

mycur = db.cursor()

@app.route('/send_data', methods=["POST"])
def send_data():
    if request.method == 'POST':
        user_id = request.form['user_Id']
        ldr_reading = request.form['ldr_reading']
        mycur.execute("INSERT INTO ldr1data (readingdate, LDRreading) VALUES (NOW(), %s)", (ldr_reading, user_id))
        db.commit()
        return "Data received successfully"
    return "Error receiving data"

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route('/signup', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        email = request.form['username']
        name = request.form['firstname']
        surname = request.form['surname']
        phonenum = request.form['phonenumber']
        address = request.form['address']
        passwrd = request.form['passwrd']
        area = request.form['area']
        mycur.execute("INSERT INTO users (email, name, surname, phonenum, address, passwrd, area) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                      (email, name, surname, phonenum, address, passwrd, area))
        db.commit()
        return redirect(url_for('userlogin'))
    return render_template("signup.html")

@app.route('/userlogin', methods=["GET", "POST"])
def userlogin():
    if request.method == 'POST':
        email = request.form['username']
        passwrd = request.form['passwrd']
        mycur.execute("SELECT email, passwrd, area FROM users WHERE email = %s AND passwrd = %s", (email, passwrd))
        results = mycur.fetchone()
        if not results:
            return render_template("login.html", error="Incorrect Login Details Entered. Please try again")
        else:
            session['email'] = email
            session['area'] = results[2]
            if session['area'] == 1:
                return redirect(url_for('dashboard1'))
            elif session['area'] == 2:
                return redirect(url_for('dashboard2'))
            else:
                return redirect(url_for('dashboard3'))
    return render_template("login.html")

@app.route('/adminlogin', methods=["GET", "POST"])
def adminlogin():
    if request.method == 'POST':
        email = request.form['username']
        passwrd = request.form['passwrd']
        mycur.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (email, passwrd))
        admin = mycur.fetchone()
        if admin:
            session['admin_logged_in'] = True  # Marking admin as logged in
            return redirect(url_for('admindashboard'))
        else:
            return render_template("adminlogin.html", error="Incorrect Login Details Entered. Please try again")
    return render_template("adminlogin.html")


def get_dashboard_data(table):
    mycur.execute(f"SELECT readingdate FROM {table} WHERE readingdate = (SELECT MAX(readingdate) FROM {table})")
    readingdatetime = mycur.fetchone()
    mycur.execute(f"SELECT LDRreading FROM {table} WHERE readingdate = (SELECT MAX(readingdate) FROM {table})")
    lastreading = mycur.fetchone()
    mycur.execute(f"SELECT LDRreading FROM {table} ORDER BY readingdate DESC LIMIT 1,1")
    secondlastreading = mycur.fetchone()
    pchange = ((lastreading[0] - secondlastreading[0]) / lastreading[0]) * 100 if secondlastreading else 0
    return readingdatetime, lastreading, pchange

@app.route('/dashboard1')
def dashboard1():
    mycur.execute("SELECT readingdate, LDRreading FROM ldr1data ORDER BY readingdate DESC LIMIT 100")
    data = mycur.fetchall()
    readingdatetime, lastreading, pchange = get_dashboard_data('ldr1data')

    labels = [row[0].strftime('%Y-%m-%d %H:%M:%S') for row in data]
    readings = [row[1] for row in data]

    return render_template("dashboard.html", 
                           dashboard_title="Dashboard 1", 
                           readingdatetime=readingdatetime, 
                           lastreading=lastreading, 
                           pchange=pchange, 
                           data=data, 
                           labels=labels, 
                           readings=readings)

@app.route('/dashboard2')
def dashboard2():
    mycur.execute("SELECT readingdate, LDRreading FROM ldr2data ORDER BY readingdate DESC LIMIT 100")
    data = mycur.fetchall()
    readingdatetime, lastreading, pchange = get_dashboard_data('ldr2data')

    labels = [row[0].strftime('%Y-%m-%d %H:%M:%S') for row in data]
    readings = [row[1] for row in data]

    return render_template("dashboard.html", 
                           dashboard_title="Dashboard 2", 
                           readingdatetime=readingdatetime, 
                           lastreading=lastreading, 
                           pchange=pchange, 
                           data=data, 
                           labels=labels, 
                           readings=readings)

@app.route('/dashboard3')
def dashboard3():
    mycur.execute("SELECT readingdate, LDRreading FROM ldr3data ORDER BY readingdate DESC LIMIT 100")
    data = mycur.fetchall()
    readingdatetime, lastreading, pchange = get_dashboard_data('ldr3data')

    labels = [row[0].strftime('%Y-%m-%d %H:%M:%S') for row in data]
    readings = [row[1] for row in data]

    return render_template("dashboard.html", 
                           dashboard_title="Dashboard 3", 
                           readingdatetime=readingdatetime, 
                           lastreading=lastreading, 
                           pchange=pchange, 
                           data=data, 
                           labels=labels, 
                           readings=readings)


@app.route('/admindashboard')
def admindashboard():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('admilogin'))

    mycur.execute("SELECT MAX(readingdate), LDRreading FROM ldr1data")
    area1lr = mycur.fetchone()
    mycur.execute("SELECT MAX(readingdate), LDRreading FROM ldr2data")
    area2lr = mycur.fetchone()
    mycur.execute("SELECT MAX(readingdate), LDRreading FROM ldr3data")
    area3lr = mycur.fetchone()

    mycur.execute("""
        SELECT readingdate,
               (SELECT LDRreading FROM ldr1data WHERE readingdate = a.readingdate) AS area1,
               (SELECT LDRreading FROM ldr2data WHERE readingdate = a.readingdate) AS area2,
               (SELECT LDRreading FROM ldr3data WHERE readingdate = a.readingdate) AS area3
        FROM (SELECT readingdate FROM ldr1data
              UNION
              SELECT readingdate FROM ldr2data
              UNION
              SELECT readingdate FROM ldr3data) a
        ORDER BY readingdate DESC LIMIT 100
    """)
    data = mycur.fetchall()

    readings1 = [row[1] for row in data]
    readings2 = [row[2] for row in data]
    readings3 = [row[3] for row in data]
    labels = [row[0].strftime('%Y-%m-%d %H:%M:%S') for row in data]

    readings = [area1lr[1], area2lr[1], area3lr[1]]
    areas = ['Area 1', 'Area 2', 'Area 3']
    mostsun = areas[readings.index(max(readings))]

    return render_template("admindashboard.html", 
                           mostsun=mostsun, 
                           area1lr=area1lr[1], 
                           area2lr=area2lr[1], 
                           area3lr=area3lr[1],
                           data=data,
                           labels=labels,
                           readings1=readings1,
                           readings2=readings2,
                           readings3=readings3)


@app.route('/home')
def home1():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

db.commit()

@app.route('/data', methods=['POST'])
def receive_data():
    if request.is_json:
        data = request.get_json()
        ldr_value = data.get('ldrValue')
        red_led_status = data.get('redLedStatus')
        green_led_status = data.get('greenLedStatus')

        # Insert LDR data into ldr1data table as an example
        connection = mysql.connector.connect()
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO ldr1data (LDRreading) VALUES (%s)", (ldr_value,))
            connection.commit()
            cursor.close()
            connection.close()

        response = {
            'status': 'success',
            'message': 'Data received',
            'data': {
                'ldrValue': ldr_value,
                'redLedStatus': red_led_status,
                'greenLedStatus': green_led_status
            }
        }
        return jsonify(response), 200
    else:
        return jsonify({'status': 'fail', 'message': 'Invalid JSON'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


