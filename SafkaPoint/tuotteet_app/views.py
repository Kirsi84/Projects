from datetime import datetime

from flask import Flask, render_template, redirect, url_for
from flask import request

import mysql.connector
from mysql.connector import errorcode

# import logging

from . import app

def getDbSettings():
    #local = (SERVER['REMOTE_ADDR']=='127.0.0.1' || SERVER['REMOTE_ADDR']=='::1')
   
    local = request.remote_addr == "127.0.0.1" or request.remote_addr == "::1"
   
    # local = 1   #### 1=localhost, 0=production
    
    if (local):
        dbSettings = {"host": "localhost", "user": "root", "password": "", "database": "noutopiste" }   
    else:
        dbSettings = {"host": "127.0.0.1:53181", "user": "azure", "password": "6#vWHD_$", "database": "noutopiste" }
    return dbSettings


# ostoslista = [[1, "hiiva", "kuivahiiva", "1.50"],
#                  [2, "leipä", "juureen leivottu", "2.50"],
#                  [3, "maito", "laktoositon", "2.2"],
#                  [4, "sitruuna", "luomu", "2.30"],
#                  [5, "sokeri", "kidesokeri", "2.50"],                
#                  [6, "vesi", "hiilihapoton", "1"],
#                  [7, "voi", "luomu", "3.2"]]


def getDBProducts():
    products = ()
    try:

        dbSet = getDbSettings()       
      
        # cnx = mysql.connector.connect(user='root', password='',
        #                       host='localhost',
        #                       database='noutopiste')

        cnx = mysql.connector.connect(user= dbSet['user'],
                              password=dbSet['password'],
                              host=dbSet['host'],
                              database=dbSet['database'])

        cursor  = cnx.cursor()
        query   = ("SELECT id, nimi, kuvaus, hinta FROM tuote order by nimi")  
        cursor.execute(query)
        result  = cursor.fetchall()

        return result

    except mysql.connector.Error as err:
        msg = ""
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            msg = "Something is wrong with your user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            msg = "Database does not exist"
        else:
            msg = err

       # writeToLog("getDBProducts: " +  msg)
    
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

        # cursor.close()
        # cnx.close()
 
    except mysql.connector.Error as err:
        msg = ""
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            msg = "Something is wrong with your user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            msg = "Database does not exist"
        else:
            msg = err

       # writeToLog("getDBProducts: " +  msg)
    
    finally:
        cursor.close()
        cnx.close()


# def writeToLog(msg):
#     logging.basicConfig(filename='log/flask_server.log' ,
#     level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
 

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
   
    if request.method == "POST":
        form_product_keys = request.form.getlist("product_keys")

        tilaukset = ""
        for product_key in form_product_keys:
           tilaukset += product_key + " " 

        return redirect(url_for('order'))
        # return render_template(
        #    'order.html',
        #    title='Tilaus',
        #    year=datetime.now().year,
        #    message=tilaukset)
    else:
       now = datetime.now()
       formatted_now = now.strftime("%d.%m.%Y klo %H:%M:%S")
        
       products = getDBProducts()

       return render_template(
            "index.html",
            title = "Tuotteet",
            message = "Valitse tuotteet listalta - " + formatted_now + " ",
            data = products)

    # return render_template("home.html")


@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
   
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
        

        now = datetime.now()
        formatted_now = now.strftime("%d.%m.%Y klo %H:%M:%S")        
        products = getDBProducts()

        return render_template(
            "index.html",
            title = "Noutopiste",
            year=datetime.now().year,
            message = "Valitse tuotteet listalta - " + formatted_now + " ",
            data = products)


@app.route('/order/')
def order():
    """Renders the about page."""
    return render_template(
        'order.html',
        title='Tilaus',
        year=datetime.now().year,
        message='Tilaus-toimintoa ei ole toteutettu'
    )
   
    # if request.method == "GET":
    #     products = getDBProducts()
    #     return render_template("order.html")
    #     #   return render_template("order.html", data = products)
    # else:
    #     form_movie_keys = request.form.getlist("movie_keys")
        # for form_movie_key in form_movie_keys:
        #     db.delete_movie(int(form_movie_key))
        # return redirect(url_for("movies_page")) 

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
