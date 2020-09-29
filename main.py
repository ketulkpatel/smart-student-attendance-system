from re import S
from flask import Flask, render_template, request, session,redirect,url_for,Response
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.schema import ForeignKey
from werkzeug.utils import secure_filename
import os
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import mysql.connector
import csv
import cv2
from camera import VideoCamera
from face_recognition_code import recognition


with open('config.json', 'r') as c:
    params = json.load(c)["params"]
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:@localhost/test'
app.secret_key = 'super secret key'
app.config['upload_folder_student']=params['upload_location_student']
app.config['upload_folder_faculty']=params['upload_location_faculty']
app.config['upload_folder_student_data']=params['upload_location_student_data']

db=SQLAlchemy(app)

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'


mydb=mysql.connector.connect(host='localhost',user='root',password='',database='test')


# Intialize MySQL
mysql = MySQL(app)
global att_data
att_data = []



class Test_faculty(db.Model):
    f_id=db.Column(db.String(11),nullable=False,primary_key=True)
    f_name = db.Column(db.String(11), nullable=False)
    f_password = db.Column(db.String(11), nullable=False)
    f_contact = db.Column(db.String(11), nullable=False)
    classes = db.relationship('Test_class', backref='test_faculty', lazy=True)

class Test_subject(db.Model):
    sub_code = db.Column(db.String(11),nullable=False,primary_key=True)
    sub_name = db.Column(db.String(11),nullable=False)
    subjects= db.relationship('Test_class', backref='test_subject', lazy=True)



class Test_student_class(db.Model):
    stu_class_id = db.Column(db.Integer, primary_key=True)
    s_id = db.Column(db.String(11),nullable=False)
    s_name = db.Column(db.String(11),nullable=False)
    s_branch = db.Column(db.String(11),nullable=False)
    s_sem = db.Column(db.Integer,nullable=False)
    s_password = db.Column(db.String(11),nullable=False)
    s_contact = db.Column(db.Integer,nullable=False)
    class_id= db.Column(db.Integer, db.ForeignKey('test_class.class_id'),nullable=False)

class Test_class(db.Model):
    class_id = db.Column(db.Integer, nullable=False, primary_key=True)
    f_id = db.Column(db.Integer, db.ForeignKey('test_faculty.f_id'),nullable=False)
    sub_code = db.Column(db.String(11), db.ForeignKey('test_subject.sub_code'),nullable=False)
    students=db.relationship('Test_student_class', backref='test_class', lazy=True)



@app.route("/")
def home():
    session.clear()
    return render_template('index.html')


@app.route("/admin", methods=['GET', 'POST'])
def signin():
    if ('user' in session and session['user']==params['admin_name']):
        return render_template('admin.html')
    if request.method == 'POST':
        uname = request.form.get('uid')
        upass = request.form.get('pass')
        if (uname == params['admin_name'] and upass == params['admin_pass']):
            session['user']=uname
            return render_template('admin.html')

    if request.method == 'POST' and 'uid' in request.form and 'pass' in request.form:
        # Create variables for easy access
        global id
        id= request.form['uid']
        password = request.form['pass']


        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM test_faculty WHERE f_id = %s AND f_password = %s', (id, password))
        # Fetch one record and return result
        fac_res = cursor.fetchone()
        # If account exists in accounts table in out database
        if fac_res:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = fac_res['f_id']
            #session['username'] = account['username']
            # Redirect to home page

            return render_template('faculty.html')
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('index.html')



@app.route("/storefacultydetails",methods=['GET', 'POST'])
def storefacultydetails():
    if request.method == "POST":
        fid=request.form.get('fid')
        fname=request.form.get('fname')
        fpassword=request.form.get('fpassword1')
        fcontact=request.form.get('fcontact')
        f = request.files['fimage']
        f.save(os.path.join(app.config['upload_folder_faculty'],secure_filename(f.filename)))
        entry_fac=Test_faculty(f_id=fid,f_name=fname,f_password=fpassword,f_contact=fcontact)
        db.session.add(entry_fac)
        db.session.commit()
    return render_template('admin.html')


@app.route("/addsubject",methods=['GET', 'POST'])
def addsubject():
    if request.method == "POST":
        sub_code=request.form.get('subcode')
        sub_name=request.form.get('subjectname')
        entry_sub = Test_subject(sub_code=sub_code,sub_name=sub_name)
        db.session.add(entry_sub)
        db.session.commit()
    return render_template('subjectform.html')

@app.route("/assignfacultysubject",methods=['GET', 'POST'])
def facultysubjects():
    if request.method == "POST":
        f_id = request.form.get('fid')
        f_subcode = request.form.get('fsubcode')
        entry_class = Test_class(f_id=f_id, sub_code=f_subcode)
        db.session.add(entry_class)
        db.session.commit()
    return render_template('assignfacultysubject.html')


@app.route("/assignstudentclass",methods=['GET', 'POST'])
def studentclass():
    if request.method == "POST":
        stu_data_csv = request.files['scsv']
        stu_data_csv.save(
            os.path.join(app.config['upload_folder_student_data'], secure_filename(stu_data_csv.filename)))
        cursor = mydb.cursor()
        csv_data = csv.reader(
            open('C:\\Users\\ketul\\PycharmProjects\\SDP-project\\Database\\StudentData\\StudentData.csv'))
        for row in csv_data:
            cursor.execute('INSERT INTO test_student_class (stu_class_id,s_id,class_id) VALUES (%s,%s,%s)', row)
        mydb.commit()
        cursor.close()
    return render_template('addstudents.html')


@app.route("/studentform")
def studentdetails():
    return render_template('studentform.html')


@app.route("/facultyform")
def facultydetails():
    return render_template('FacultyForm.html')

@app.route("/subjectform")
def subjectdetails():
    return render_template('subjectform.html')

@app.route("/attendance")
def attendance():
    return redirect(url_for('takeattendance', f_id=id))

@app.route("/takeattendance/<string:f_id>", methods=['GET', 'POST'])
def takeattendance(f_id):
    cursor = mysql.connection.cursor()
    data = cursor.execute("select sub_name from test_subject as sub INNER JOIN test_class as cla on sub.sub_code=cla.sub_code where cla.f_id= %s",[f_id])

    return render_template('takeattendance.html', subject0=[ x[0] for x in cursor.fetchall()],fid=f_id)






@app.route("/addnewstudentphoto")
def addnewstudentphoto():
    return render_template('addstudentphoto.html')

@app.route("/studentphoto",methods=['GET', 'POST'])
def studentphoto():
    global stu_id
    stu_id=request.form.get('sid')
    return redirect(url_for('addstudentphoto',stuid=stu_id))

@app.route("/addstudentphoto/<string:stuid>")
def addstudentphoto(stuid):
    cam = cv2.VideoCapture(0)

    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    count = 0
    while(True):
        ret, img = cam.read()
        faces = face_detector.detectMultiScale(img, 1.3, 5)
        for (x,y,w,h) in faces:
            x1 = x
            y1 = y
            x2 = x+w
            y2 = y+h
            cv2.rectangle(img, (x1,y1), (x2,y2), (255,255,255), 2)
            count += 1
            cv2.imwrite("Database/"+ stuid + ".jpg", img[y1:y2,x1:x2])
            cv2.imshow('image', img)
        k = cv2.waitKey(200) & 0xff
        if k == 27:
            break
        elif count >= 1:
             break
    cam.release()
    cv2.destroyAllWindows()
    return render_template('addstudentphoto.html')



@app.route('/startattendance')
def startattendance():

    input_embedding=recognition.create_input_image_embeddings()
    name,faces=recognition.recognize_faces_in_cam(input_embedding)
    print(name)
    print(faces)
    att_data.append(name)
    return redirect(url_for('takeattendance', f_id=id))


@app.route('/closeattendance')
def closeattendance():
    print(att_data)
    with open('my_csv.csv', 'w', newline='') as f:
        w = csv.writer(f)
        for i in range(len(att_data)):
            w.writerow([i+1,att_data[i]])

    return render_template('faculty.html')

app.run(debug=True)