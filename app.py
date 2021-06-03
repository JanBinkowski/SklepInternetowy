from flask import Flask, render_template, request, json, session
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
    return render_template('home.html')

@app.route('/register')
def form():
    return render_template('form.html')

@app.route('/signIn')
def signIn():
    return render_template('signIn.html')

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

                return render_template('/userHome.html', userName = login)
            else:
                return render_template('error.html', error='Wrong Login or Password.')
        else:
            return render_template('error.html', error='Wrong Login or Password.')

    except Exception as e:
        return render_template('error.html', error=str(e))

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

        hashed_haslo = generate_password_hash(haslo)

        cursor = mysql.connection.cursor()

        args = [imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu]
        # cursor.callproc('dodaj_uzytkownika', (imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu))

        cursor.execute('''INSERT INTO Dane_uzytkownika (imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');'''%(imie, nazwisko, login, hashed_haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu))
        # cursor.execute('''CALL dodaj_uzytkownika('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');'''%(imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu))

        mysql.connection.commit()
        cursor.close()
        return f"Done!!"

app.run(host='localhost', port=5000)