# member sign up 
# step1 
# import flask module
from flask import *

# import pymysql module 
import pymysql
import pymysql.cursors

# import os
# it helps to interact with the machine
import os

# step 3  
# initialise the app 
app =Flask(__name__)

# we need cross origin resource sharing 
from flask_cors import CORS
CORS()


app.config['UPLOAD_FOLDER']='/home/254JasonMbugua/mysite/static/images'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# step 4
# define the rote /epdpoint
@app.route ("/api/signup" , methods = ['post'])

# define the function
def signup():

    # get user inputs from the form 
    username=request.form["username"]
    password=request.form['password']
    email=request.form['email']
    phone=request.form['phone']
    # establish connection to database
    # we are going to use pymysql module
    connection = pymysql.connect(host='254JasonMbugua.mysql.pythonanywhere-services.com',user='254JasonMbugua',password='user1234',database='254JasonMbugua$default')
    # step 6 
    # define your cursor 
    cursor = connection.cursor()
    # step7 
    # define the sql to inser users

    sql ='insert into users(username,password,email,phone)  values(%s,%s,%s,%s)'

    # step8 
    # define you data
    # these are the user input from the form
    # we put then in a tuple
    data= (username , password , email, phone)

    # run the query 
    # also called executing 

    cursor.execute(sql,data)

    # step 10 
    # commit /save the user 
    connection.commit()

    # step 11 
    # give user a response upon a successful sign up 
    return jsonify({"message":"sign up successful"})


# member signin

@app.route('/api/signin',methods =["POST"])
# define the function
def signin():
    # get user input 
    email=request.form['email']
    password=request.form['password']
    connection = pymysql.connect ( host ='254JasonMbugua.mysql.pythonanywhere-services.com',user='254JasonMbugua' ,password='user1234', database='254JasonMbugua$default')

    # define a cursor 
    cursor = connection .cursor(pymysql.cursors.DictCursor)
    # define your sql  to select
    sql = "select *  from users where email =% s and password =%s"

    # define the data 
    # these are the user inputs from the form 
    data = ( email, password )
    # execute/run the query 
    cursor.execute(sql, data)

    # check if user exists
    if  cursor.rowcount == 0:
        return jsonify({"message": "login failed"})

    else:
        # get user info upon ogin successful 
        user=cursor.fetchone()
        return jsonify({"message": "log in successful","user": user })


# add products  
# define a route /end point 
@app.route("/api/add_products", methods =['POST'])

# DEFINE THE NAME OF THE FUNCTION 
def add_product():
    # get user inputs from the form
    product_name =request.form["product_name"]
    product_description= request.form["product_description"]
    product_cost =request.form["product_cost"]
    product_photo=request.files["product_photo"]

    # get the original name of the uploaded image file
    filename =product_photo.filename
    # print(filename) 

    # create a full path where the image will be saved
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)

    # step 5
    # save the uploaded file in the pecified path
    product_photo.save(photo_path)
    # establish connection to the database 
    connnection=pymysql.connect(host='254JasonMbugua.mysql.pythonanywhere-services.com', user='254JasonMbugua', password=' user1234',database='254JasonMbugua$default')

    # define the cursor
    cursor=connnection.cursor()
    # define sql to insert products 
    sql ="insert into products(product_name ,product_description,product_cost,product_photo ) values ( %s,%s,%s,%s)"

    # define your data       
    # this are the inputs from the form
    # NB:we will put filename for product_photo
    data = (product_name,product_description,product_cost,filename)

    # execute/run the query
    cursor.execute(sql,data)

    # commit changes
    connnection.commit()
    # return response to the user 
    return jsonify ({"mesage":"product added successful"})



# get all products
@app.route("/api/products_details" ,methods=["GET"])

def products():
    connection=pymysql.connect( host="254JasonMbugua.mysql.pythonanywhere-services.com", user="254JasonMbugua",password="user1234",database="254JasonMbugua$default")
    # define your cursor 
    cursor=connection.cursor(pymysql.cursors.DictCursor)

    # define sql 
    sql="select * from products"
    # execute 
    cursor.execute(sql)
    # fetch all products 
    allproducts= cursor.fetchall()

    return jsonify(allproducts )

# Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret 
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
        # Create a POST Request to above url, providing headers, payload 
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) # 
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})





    
   

# step 12 
# run the application
app.run(debug =True)