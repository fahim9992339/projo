from flask import Flask, request, jsonify
import pymysql
import pymysql.cursors
import os
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = '/home/254JasonMbugua/mysite/static/images'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# SIGNUP ROUTE
@app.route("/api/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    phone = request.form["phone"]

    connection = pymysql.connect(
        host='Fahim999gt.mysql.pythonanywhere-services.com',
        user='254JasonMbugua',
        password='user1234',
        database='254JasonMbugua$default'
    )

    cursor = connection.cursor()
    sql = 'INSERT INTO users(username, password, email, phone) VALUES (%s, %s, %s, %s)'
    data = (username, password, email, phone)
    cursor.execute(sql, data)
    connection.commit()

    return jsonify({"message": "sign up successful"})


# SIGNIN ROUTE
@app.route("/api/signin", methods=["POST"])
def signin():
    email = request.form["email"]
    password = request.form["password"]

    connection = pymysql.connect(
        host='Fahim999gt.mysql.pythonanywhere-services.com',
        user='254JasonMbugua',
        password='user1234',
        database='254JasonMbugua$default'
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM users WHERE email = %s AND password = %s"
    data = (email, password)
    cursor.execute(sql, data)

    if cursor.rowcount == 0:
        return jsonify({"message": "login failed"})
    else:
        user = cursor.fetchone()
        return jsonify({"message": "log in successful", "user": user})


# ADD PRODUCT ROUTE
@app.route("/api/add_products", methods=["POST"])
def add_product():
    product_name = request.form["product_name"]
    product_description = request.form["product_description"]
    product_cost = request.form["product_price"]
    product_photo = request.files["product_photo"]

    # Save photo
    filename = product_photo.filename
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    product_photo.save(photo_path)

    connection = pymysql.connect(
        host='Fahim999gt.mysql.pythonanywhere-services.com',
        user='254JasonMbugua',
        password='user1234',
        database='254JasonMbugua$default'
    )

    cursor = connection.cursor()
    sql = "INSERT INTO products(product_name, product_description, product_cost, product_photo) VALUES (%s, %s, %s, %s)"
    data = (product_name, product_description, product_cost, filename)
    cursor.execute(sql, data)
    connection.commit()

    return jsonify({"message": "product added successful"})


# GET ALL PRODUCTS
@app.route("/api/products_details", methods=["GET"])
def products():
    connection = pymysql.connect(
        host='Fahim999gt.mysql.pythonanywhere-services.com',
        user='254JasonMbugua',
        password='user1234',
        database='254JasonMbugua$default'
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM products"
    cursor.execute(sql)
    allproducts = cursor.fetchall()

    return jsonify(allproducts)


# MPESA PAYMENT
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route("/api/mpesa_payment", methods=["POST"])
def mpesa_payment():
    amount = request.form["amount"]
    phone = request.form["phone"]

    consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
    consumer_secret = "amFbAoUByPV2rM5A"

    # Get access token
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = response.json()
    access_token = "Bearer " + data["access_token"]

    # Generate password
    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    business_short_code = "174379"
    data_to_encode = business_short_code + passkey + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()

    # STK Push payload
    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1",  # Use 1 for testing
        "PartyA": phone,
        "PartyB": business_short_code,
        "PhoneNumber": phone,
        "CallBackURL": "https://coding.co.ke/api/confirm.php",
        "AccountReference": "SokoGarden Online",
        "TransactionDesc": "Payments for Products"
    }

    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }

    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(stk_url, json=payload, headers=headers)

    return jsonify({"message": "An MPESA Prompt has been sent to your phone. Please check and complete payment."})


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)
