from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

# mysql database items
import mysql.connector
from mysql.connector import errorcode

from . import app    

def writeIntoLogFile(msg):
    filename = "./logs/safkapoint.log"    
    # now = datetime.now()
    # formatted_now = now.strftime("%d.%m.%Y klo %H:%M:%S")      
    formatted_now  = getDate()
    f = open(filename,"a")
    f.write(formatted_now + ":::" + msg +"\n")
    f.close()

def getDate():
    now = datetime.now()
    return now.strftime("%d.%m.%Y klo %H:%M:%S")

writeIntoLogFile("Just testing!")  # Just a test
    
def getDbSettings():
    #local = (SERVER['REMOTE_ADDR']=='127.0.0.1' || SERVER['REMOTE_ADDR']=='::1')
   
    local = request.remote_addr == "127.0.0.1" or request.remote_addr == "::1"
   
    # local = 1   #### 1=localhost, 0=production
    
    if (local):
        dbSettings = {"host": "localhost", "user": "root", "password": "", "database": "noutopiste" }   
    else:
        dbSettings = {"host": "", "user": "", "password": "", "database": "noutopiste" }
    return dbSettings

def getDBProductsByIdList(product_keys):
    products = ()
    try:
        sqlwhere = ""
        if len(product_keys) > 0:
            sqlwhere =  ','.join([str(x) for x in product_keys])

            sqlwhere =  "WHERE id in (" + sqlwhere + " ) "

        dbSet = getDbSettings()       
      
        cnx = mysql.connector.connect(user= dbSet['user'],
                              password=dbSet['password'],
                              host=dbSet['host'],
                              database=dbSet['database'])

        cursor  = cnx.cursor()

        if sqlwhere == "":
            query   = ("SELECT id, nimi, kuvaus, hinta FROM tuote ORDER BY nimi")
        else:
            query   = ("SELECT id, nimi, kuvaus, hinta FROM tuote " + sqlwhere + "  ORDER BY nimi")


        cursor.execute(query)
     
        columns = cursor.description 
        result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
       
        return result

    except mysql.connector.Error as err:
        msg = ""
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            msg = "Something is wrong with your user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            msg = "Database does not exist"
        else:
            msg = err._full_msg

        writeIntoLogFile("getDBProductsByIdList: " +  msg)
          
    finally:
        cursor.close()
        cnx.close()


def getDBProducts():
    products = ()
    try:

        dbSet = getDbSettings()       
      
        cnx = mysql.connector.connect(user= dbSet['user'],
                              password=dbSet['password'],
                              host=dbSet['host'],
                              database=dbSet['database'])

        cursor  = cnx.cursor()
        query   = ("SELECT id, nimi, kuvaus, hinta FROM tuote order by nimi")  
        cursor.execute(query)
     
        columns = cursor.description 
        result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
       
        return result

    except mysql.connector.Error as err:
        msg = ""
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            msg = "Something is wrong with your user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            msg = "Database does not exist"
        else:
            msg = err._full_msg

        writeIntoLogFile("getDBProducts: " +  msg)
          
    finally:
        cursor.close()
        cnx.close()

def updateDBProduct(name, description, price):
    try:
        dbSet = getDbSettings()       
      
        cnx = mysql.connector.connect(user= dbSet['user'],
                              password=dbSet['password'],
                              host=dbSet['host'],
                              database=dbSet['database'])

        cursor  = cnx.cursor()
        sql = ("INSERT INTO tuote "
               "(nimi, kuvaus, hinta) "
               "VALUES (%s, %s, %s)")

        sql_data = (name, description, price)

        # Insert new product
        cursor.execute(sql, sql_data)
        emp_no = cursor.lastrowid
    
        # Make sure data is committed to the database
        cnx.commit()
 
    except mysql.connector.Error as err:
        msg = ""
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            msg = "Something is wrong with your user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            msg = "Database does not exist"
        else:
            msg = err._full_msg

        writeIntoLogFile("updateDBProduct: " +  msg)
    
    finally:
        cursor.close()
        cnx.close()


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    try:
        if request.method == "POST":

            form_product_keys = request.form.getlist("product_keys")
            if len(form_product_keys) > 0:

                formatted_now  = getDate()
 
                orders = getDBProductsByIdList(form_product_keys)
            
                return render_template(
                    "order.html",
                        title = "Tilaukset",
                        year=datetime.now().year,
                        message = "Tilatut tuotteet - " + formatted_now + " ",
                        data = orders)
            else:
                formatted_now  = getDate()
                    
                products = getDBProducts()
                
                return render_template(
                        "index.html",
                        title = "Tuotteet",
                        year=datetime.now().year,
                        message = "Valitse tuotteet listalta (valitse vähintään yksi) - " + formatted_now + " ",
                        data = products)
   
        else:

            formatted_now  = getDate()
                
            products = getDBProducts()
            
            return render_template(
                    "index.html",
                    title = "Tuotteet",
                    year=datetime.now().year,
                    message = "Valitse tuotteet listalta - " + formatted_now + " ",
                    data = products)

    except Exception as e:
        writeIntoLogFile("home: " + str(e))
        return redirect(url_for('customerror'))

@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    try:
        if request.method == "GET":
            return render_template(
                    "addProduct.html",
                    title = "Lisää tuote",
                    year=datetime.now().year,
                    message = "Tuotteen tiedot "
                    )
        else:
            name = request.form["nimi"]
            description = request.form["kuvaus"]
            price = request.form["hinta"]
            
            updateDBProduct(name, description, price)
            
            return redirect(url_for('home'))
         
    except Exception as e:
        writeIntoLogFile("addProduct" + str(e))
        return redirect(url_for('customerror'))


@app.route('/order', methods=['GET', 'POST'])
def order():
    """Renders the order page."""
    try:
        return render_template(
            'order.html',
            title='Tilaus',
            year=datetime.now().year,
            message='Tilaus-toimintoa ei ole toteutettu'
        )
    except Exception as e:
        writeIntoLogFile("order: " + str(e))
        return redirect(url_for('customerror'))


@app.route('/contact/')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Yhteystiedot',
        year=datetime.now().year,
        message='Tervetuloa!'
    )

@app.route('/about/')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='Tietoja',
        year=datetime.now().year,
        message='Python/Flask'
    )


@app.route('/customerror', methods=['GET'])
def customerror():
    """Renders the error page."""
    return render_template(
        'customerror.html',
        title='Virhe',
        year=datetime.now().year,
        message='Kokeile hetken kuluttua uudelleen!'
    )
