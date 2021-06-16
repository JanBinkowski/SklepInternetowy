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

@app.route('/addressEdit')
def addressEdit():
    if session.get('user'):
        return render_template('addressEdit.html')
    else:
        return render_template('error.html', error = "In order to change your address, first log in")

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
        print(data[0][0])
        sellerID = data[0][0]
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category = request.form['categories']

        # price = price.replace(",", ".")

        categoryID = 1
        if category == 'Electronics':
            categoryID = 1
        if category == 'Clothes':
            categoryID = 2
        if category == 'Kitchen utensils':
            categoryID = 3
        if category == 'Pets':
            categoryID = 4
        if category == 'Car parts':
            categoryID = 5
        print(name, price, description, categoryID, sellerID)
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
            return render_template('error.html', error='Please repeat password correctly!')


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


@app.route('/showSoldProducts', methods = ['POST', 'GET'])
def showSoldProducts():
    if session.get('user'):
        return render_template('error.html', error = "")
    else:
        return render_template('error.html', error = "First log in")


@app.route('/showProductsPutForSale', methods = ['POST', 'GET'])
def showProductsPutForSale():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute("Select Sprzedajacy_ID from Sprzedajacy where Dane_ID = '%s' " %(session.get('user')))
        data1 = cursor.fetchall()


        cursor.execute("Select Produkt_ID, nazwa, cena from Produkt where Sprzedajacy_ID = '%s' and czyDostepny=1; " % (data1[0][0]))
        data = cursor.fetchall()

        return render_template('productsPutForSale.html', data=data)
    else:
        return render_template('error.html', error = "First log in")

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

@app.route('/addressEditRequest', methods = ['POST', 'GET'])
def addressEditRequest():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        panstwo = request.form['panstwo']
        miasto = request.form['miasto']
        wojewodztwo = request.form['wojewodztwo']
        ulica = request.form['ulica']
        kod_pocztowy = request.form['kod_pocztowy']
        numer_domu = request.form['numer_domu']
        numer_mieszkania = request.form['numer_mieszkania']
        cursor.execute(
            ''' update Dane_uzytkownika set panstwo = '%s', miasto = '%s', wojewodztwo = '%s', ulica = '%s', kod_pocztowy = '%s', numer_domu = '%s', numer_mieszkania = '%s' WHERE Dane_ID = '%s' ''' %(panstwo, miasto, wojewodztwo, ulica, kod_pocztowy, numer_domu, numer_mieszkania, session['user']))
        mysql.connection.commit()
        cursor.close()
        return render_template('error.html', error = "You have changed your delivery address.")
    else:
        return render_template('error.html', error = "First log in.")

@app.route('/showBoughtProducts', methods = ['POST', 'GET'])
def showBoughtProducts():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute("Select Kupujacy_ID from Kupujacy where Dane_ID = '%s' " %(session.get('user')))
        data1 = cursor.fetchall()
        cursor.execute("""SELECT Produkt_ID, nazwa, cena from Produkt where Produkt_ID in
                          (SELECT Produkt_Produkt_ID from Zamowienie_Produkt WHERE Zamowienie_Zamowienie_ID in
                          (SELECT Zamowienie_ID from Zamowienie WHERE Kupujacy_ID = '%s'))""" %(data1[0][0]))
        data2 = cursor.fetchall()
        print(data2)

        cursor.execute("""SELECT status from Zamowienie where Zamowienie_ID in
                          (SELECT Zamowienie_Zamowienie_ID from Zamowienie_Produkt WHERE Produkt_Produkt_ID in
                          (SELECT Produkt_Produkt_ID from Zamowienie_Produkt WHERE Zamowienie_Zamowienie_ID in
                          (SELECT Zamowienie_ID from Zamowienie WHERE Kupujacy_ID = '%s')));""" % (data1[0][0]))
        data = cursor.fetchall()
        if (len(data) > 0):
            new_tuple = ((data2[0][0], data2[0][1], data2[0][2], data[0][0]),)
            for i in range(1, len(data)):
                new_tuple = new_tuple + ((data2[i][0], data2[i][1], data2[i][2], data[i][0]),)
        else:
            return render_template('error.html', error = "You haven't bought anything yet.")
        print(new_tuple)
        return render_template('productsBought.html', data = new_tuple)
    else:
        return render_template('error.html', error = "First log in")

@app.route('/payForProduct',  methods = ['POST', 'GET'])
def payForProduct():
    if session.get('user'):
        price = request.form['price']
        cursor = mysql.connection.cursor()
        cursor.execute("Select Kupujacy_ID from Kupujacy where Dane_ID = '%s' " %(session.get('user')))
        data1 = cursor.fetchall()
        cursor.execute("""SELECT Produkt_Produkt_ID from Zamowienie_Produkt WHERE Zamowienie_Zamowienie_ID in
                          (SELECT Zamowienie_ID from Zamowienie WHERE Kupujacy_ID = '%s')""" %(data1[0][0]))
        data2 = cursor.fetchall()
        helpTup = (int(price),)
        print(helpTup)
        print(data2)
        if (helpTup in data2):
            cursor.execute("""select status from Zamowienie where Zamowienie_id in
                             (select Zamowienie_Zamowienie_ID from Zamowienie_Produkt where Produkt_Produkt_ID = '%s') """ %(price))
            status = cursor.fetchall()
            if (status[0][0] == 'Nieoplacone'):
                cursor.execute("""update Zamowienie set status = 'Oplacone' where Zamowienie_id in
                                 (select Zamowienie_Zamowienie_ID from Zamowienie_Produkt where Produkt_Produkt_ID = '%s')""" %(price))
                mysql.connection.commit()
                return render_template('error.html', error = "Simulation of paying... You have successfully paid for ordered product!")
            else:
                return render_template('error.html', error = "This order has already been paid for.")
        else:
            return render_template('error.html', error = "This products wasn't bought by you!")
    else:
        return render_template('error.html', error = "Log in first")


@app.route('/selectProduct', methods=['POST', 'GET'])
def selectProduct():
    if session.get('user'):
        return render_template("selectProduct.html")
    else:
        return render_template('error.html', error="Register and log in before selling product")

@app.route('/sendSelectRequest', methods=['POST', 'GET'])
def sendSelectRequest():

    if request.method == 'GET':
       return "Something went wrong"

    if request.method == 'POST':
        category = request.form['categories']

        if category == 'Electronics':
            categoryID = 1
        if category == 'Clothes':
            categoryID = 2
        if category == 'Kitchen utensils':
            categoryID = 3
        if category == 'Pets':
            categoryID = 4
        if category == 'Car parts':
            categoryID = 5

    cursor = mysql.connection.cursor()
    cursor.execute("Select Produkt_ID, nazwa, cena from Produkt where Kategoria_Kategoria_ID = '%s' and czyDostepny=1; " % (categoryID))
    data = cursor.fetchall()

    return render_template('showProduct.html', data=data)

@app.route('/sendSelect', methods=['POST', 'GET'])
def sendSelect():
    if request.method == 'GET':
        return "Something went wrong"

    if request.method == 'POST':
        price = request.form['price']

        cursor = mysql.connection.cursor()
        cursor.execute("Select * from Produkt where Produkt_ID = '%s'; " % (price))
        data = cursor.fetchall()
        print(data)
        idProduktu = data[0][0]
        name = data[0][1]
        cena = data[0][2]
        print(cena)
        opis = data[0][3]
        session['idProduktu'] = idProduktu
        return render_template('showDetails.html', name=name, cena=cena, opis=opis, idProduktu=idProduktu)

@app.route('/Buy', methods=['POST', 'GET'])
def Buy():
    if request.method == 'GET':
        return "Something went wrong"

    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''	select * from Dane_uzytkownika where Dane_ID = '%s' ;''' % (session['user']))
        data = cursor.fetchall()
        dane_id = data[0][0]
        cursor.execute(
            '''	select * from Kupujacy where Dane_ID = '%s' ;''' % (dane_id))
        data1 = cursor.fetchall()
        id_kupujacego = data1[0][0]
        print(id_kupujacego)
        idProduktu = session.get('idProduktu', None)
        print(idProduktu)
        cursor = mysql.connection.cursor()
        cursor.callproc('zlozZamowienie',
                      [idProduktu, id_kupujacego])
        mysql.connection.commit()
        cursor.close()
        cursor = mysql.connection.cursor()
        cursor.execute("Select * from Produkt where Produkt_ID = '%s'; " % (idProduktu))
        data = cursor.fetchall()
        name = data[0][1]
        cena = data[0][2]
        print(cena)
        opis = data[0][3]
        return render_template('bought.html', name=name, cena=cena, opis=opis)

@app.route('/Changeproduct', methods=['POST', 'GET'])
def ChangeProduct():
    if request.method == 'GET':
        return "Something went wrong"

    if request.method == 'POST':
        return render_template('selectProduct.html')

@app.route('/gotohome', methods=['POST', 'GET'])
def gotohome():
    if request.method == 'GET':
        return "Something went wrong"

    if request.method == 'POST':
        return render_template('homeLogged.html')

@app.route('/seeallorders', methods=['POST', 'GET'])
def seeallorders():
    if request.method == 'GET':
        return "Something went wrong"

    if request.method == 'POST':
        user_id = session.get('user')

    return render_template('homeLogged.html')

app.run(host='localhost', port=5000)