from flask import Flask, render_template, request, session, flash
from flask_mysqldb import MySQL
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['MYSQL_HOST'] = '34.116.254.11'
app.config['MYSQL_USER'] = 'jan-binkowski'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sklep'

mysql = MySQL(app)
app.secret_key = 'why would I tell you my secret key?'

@app.route('/')
def home():
    if session.get('user'):
        return render_template('homeLogged.html')
    else:
        return render_template('home.html')

@app.route('/register')
def form():
    return render_template('form.html')

@app.route('/signIn')
def signIn():
    return render_template('signIn.html')

@app.route('/passwordChange')
def passwordChange():
    if session.get('user'):
        return render_template('passwordChange.html')
    else:
        return render_template('error.html', error = 'Log in if you want to change your password')

@app.route('/editProfile', methods=['GET'])
def editProfile():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''	select * from Dane_uzytkownika where Dane_ID = '%s' ;''' %(session['user']))
        data = cursor.fetchall()
        imie = data[0][1]
        nazwisko = data[0][2]
        panstwo = data[0][5]
        miasto = data[0][6]
        wojewodztwo = data[0][7]
        ulica = data[0][8]
        kod = data[0][9]
        nrDomu = data[0][10]
        nrMieszkania = data[0][11]
        cursor.close()
        return render_template('editProfile.html', name=imie, surname=nazwisko, country=panstwo, city=miasto, voivodeship=wojewodztwo, street=ulica, zip=kod, house=nrDomu, appno=nrMieszkania)
    else:
        return render_template('error.html', error='Log in if you want to edit your profile.')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error='Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        login = request.form['inputLogin']
        haslo = request.form['inputPassword']

        cursor = mysql.connection.cursor()
        # cursor.callproc('sprawdz_login', (login,haslo,))
        cursor.execute(
            '''	select * from Dane_uzytkownika where login = '%s';''' % (
            login, ))

        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][4]), haslo):
                session['user'] = data[0][0]

                return redirect('/')
            else:
                return render_template('error.html', error='Wrong Login or Password.')
        else:
            return render_template('error.html', error='Wrong Login or Password.')

    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/sellProduct')
def sellProduct():
    if session.get('user'):
        return render_template("sellProduct.html")
    else:
        return render_template('error.html', error="Register and log in before selling product")

@app.route('/sendSellRequest', methods=['POST', 'GET'])
def sendSellRequest():
    if request.method == 'GET':
        return "Something went wrong"

    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''	select * from Sprzedajacy where Dane_ID = '%s' ;''' %(session['user']))
        data = cursor.fetchall()
        sellerID = data[0][0]
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category = request.form['categories']

        categoryID = 1
        if category == 'Electronics':
            categoryID = 1
        if category == 'Clothes':
            categoryID = 2
        if category == 'Kitchen utensils':
            categoryID = 3
        
        cursor.callproc('dodajProdukt',[name, price, description, categoryID, 1, sellerID])
        mysql.connection.commit()
        cursor.close()

        return render_template('error.html', error='Your product has been added for sale.')
        

@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    if request.method == 'GET':
        return "Login via the login Form"

    if request.method == 'POST':
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        login = request.form['login']
        haslo = request.form['haslo']
        panstwo = request.form['panstwo']
        miasto = request.form['miasto']
        wojewodztwo = request.form['wojewodztwo']
        ulica = request.form['ulica']
        kod_pocztowy = request.form['kod_pocztowy']
        numer_domu = request.form['numer_domu']
        numer_mieszkania = request.form['numer_mieszkania']
        hasloConfirm = request.form['hasloConfirm']

        hashed_haslo = generate_password_hash(haslo)
        hashed_hasloConfirm = generate_password_hash(hasloConfirm)
        if (haslo == hasloConfirm):
            cursor = mysql.connection.cursor()

            cursor.callproc('dodaj_uzytkownika',[imie, nazwisko, login, hashed_haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu, numer_mieszkania])

            mysql.connection.commit()
            cursor.close()
            flash('Congratulations, you are now a registered user!')
            return render_template('error.html', error='Congratulation, now you are registered!')
        else:
            return render_template('error.html', error='Password and confirmation does not match!')


@app.route('/profile', methods=['GET'])
def profileInfo():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''	select * from Dane_uzytkownika where Dane_ID = '%s' ;''' %(session['user']))
        data = cursor.fetchall()
        imie = data[0][1]
        return render_template('profile.html', name=imie)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/passwordChangeRequest', methods=['POST', 'GET'])
def passwordChangeRequest():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''	select * from Dane_uzytkownika where Dane_ID = '%s' ;''' %(session['user']))
        data = cursor.fetchall()
        currentPasswordHashed = data[0][4]
        passwordConfirm = request.form['newpassconfirm']
        newPassword = request.form['newpass']
        oldpass = request.form['oldpass']
        if check_password_hash(str(data[0][4]), oldpass) and passwordConfirm == newPassword:
            hashedPassword = generate_password_hash(newPassword)
            cursor.execute(
            ''' update Dane_uzytkownika set haslo = '%s' where Dane_ID = '%s' ; ''' %(hashedPassword, session['user']))
            mysql.connection.commit()
            cursor.close()
            return render_template('error.html', error = "You have succesfully changed your password.")
        else:
            return render_template('error.html', error = "You have either provided a wrong old password or new password and password confirmation doesn't match. Try again")
    else:
        return render_template('error.html', error = ":D :D :D nice try")

app.run(host='localhost', port=5000)