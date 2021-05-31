
from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '34.116.254.11'
app.config['MYSQL_USER'] = 'jan-binkowski'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sklep'
# app.config['MYSQL_PORT'] = '3306'
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register')
def form():
    return render_template('form.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
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

        cursor = mysql.connection.cursor()

        args = [imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu]
        cursor.callproc('dodaj_uzytkownika', args)

        # cursor.execute('''INSERT INTO Dane_uzytkownika (imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');'''%(imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu))
        # cursor.execute('''CALL dodaj_uzytkownika('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');'''%(imie, nazwisko, login, haslo, panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu))

        mysql.connection.commit()
        cursor.close()
        return f"Done!!"

app.run(host='localhost', port=5000)