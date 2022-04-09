from crypt import methods
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route("/addnewemp", methods=['GET','POST'])
def diradd():
    return render_template("AddNewEmp.html")

@app.route("/getempdata", methods=['GET','POST'])
def dirget():
    return render_template("GetEmpData.html")

@app.route("/empatt", methods=['GET','POST'])
def diratt():
    return render_template("EmpAtt.html")

@app.route("/payroll", methods=['GET','POST'])
def dirpay():
    return render_template("Payroll.html")

@app.route("/empatt", methods=['POST'])
def EmpAtt():
    now = datetime.datetime.now()
    now.strftime("%y-%m-%d %H:%M:%S")

    emp_id = request.form['emp_id']
    chkin = request.form['chkin']
    chkout = request.form['chkout']
    insert_sql = "INSERT INTO employee VALUES where emp_id = emp_id (%s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (chkin,chkout))
        db_conn.commit()

    except Exception as e:
            return str(e)

    finally:
        cursor.close()

    return render_template('Home.html')


@app.route("/fetchdata", methods=['POST'])
def GetEmpData():
    emp_id = request.form["emp_id"]
    mycursor = db_conn.cursor()
    mycursor.execute("select * from employee where emp_id = emp_id")
    mycursor.fetchall()
    
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    s3 = boto3.resource('s3')
    s3_Object = s3.Bucket(custombucket).Object(emp_image_file_name_in_s3).get()
    image = s3_Object['Body'].read().decode()
    bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
    s3_location = (bucket_location['LocationConstraint'])
    print(mycursor,image)
    return render_template('GetNewEmpOut.html')



@app.route("/addemp", methods=['GET','POST'])
def AddNewEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    contact_no = request.form['contact_no']
    email = request.form['email']
    position = request.form['position']
    hiredate = request.form['hiredate']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, contact_no, email, position, hiredate, salary))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddNewEmpOut.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

