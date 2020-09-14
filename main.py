from flask import Flask, render_template, request, session
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import pymysql
import os


with open('config.json', 'r') as c:
    params = json.load(c)["params"]
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:@localhost/test'
app.secret_key = 'super secret key'
app.config['upload_folder_student']=params['upload_location_student']
app.config['upload_folder_faculty']=params['upload_location_faculty']
db=SQLAlchemy(app)


class Test_student(db.Model):
    s_id=db.Column(db.String(11),nullable=False,primary_key=True)
    s_fname = db.Column(db.String(11), nullable=False)
    s_lname = db.Column(db.String(11), nullable=False)
    s_password = db.Column(db.String(11), nullable=False)
    s_contact = db.Column(db.Integer, nullable=False)
    stu_classes= db.relationship('Test_student_class', backref='test_student', lazy=True)

class Test_faculty(db.Model):
    f_id=db.Column(db.String(11),nullable=False,primary_key=True)
    f_fname = db.Column(db.String(11), nullable=False)
    f_lname = db.Column(db.String(11), nullable=False)
    f_password = db.Column(db.String(11), nullable=False)
    f_contact = db.Column(db.String(11), nullable=False)
    classes = db.relationship('Test_class', backref='test_faculty', lazy=True)

class Test_subject(db.Model):
    sub_code = db.Column(db.String(11),nullable=False,primary_key=True)
    sub_name = db.Column(db.String(11),nullable=False)
    subjects= db.relationship('Test_class', backref='test_subject', lazy=True)



class Test_student_class(db.Model):
    stu_class_id = db.Column(db.Integer, primary_key=True)
    s_id = db.Column(db.String(11), db.ForeignKey('test_student.s_id'),nullable=False)
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
    return render_template('index.html')


@app.route("/storestudentdetails",methods=['GET', 'POST'])
def storestudentdetails():
    if request.method == "POST":
        sid=request.form.get('sid')
        sfname=request.form.get('sfname')
        slname=request.form.get('slname')
        spassword=request.form.get('spassword1')
        scontact=request.form.get('scontact')
        f = request.files['simage']
        f.save(os.path.join(app.config['upload_folder_student'],secure_filename(f.filename)))
        entry=Test_student(s_id=sid,s_fname=sfname,s_lname=slname,s_password=spassword,s_contact=scontact)
        db.session.add(entry)
        db.session.commit()
    return render_template('admin.html')


@app.route("/storefacultydetails",methods=['GET', 'POST'])
def storefacultydetails():
    if request.method == "POST":
        fid=request.form.get('fid')
        ffname=request.form.get('ffname')
        flname=request.form.get('flname')
        fpassword=request.form.get('fpassword1')
        fcontact=request.form.get('fcontact')
        f = request.files['fimage']
        f.save(os.path.join(app.config['upload_folder_faculty'],secure_filename(f.filename)))
        entry_fac=Test_faculty(f_id=fid,f_fname=ffname,f_lname=flname,f_password=fpassword,f_contact=fcontact)
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
        f_id=request.form.get('fid')
        f_subcode = request.form.get('fsubcode')
        entry_class=Test_class(f_id=f_id,sub_code=f_subcode)
        db.session.add(entry_class)
        db.session.commit()
    return render_template('assignfacultysubject.html')


@app.route("/assignstudentclass",methods=['GET', 'POST'])
def studentclass():
    if request.method == "POST":
        s_id = request.form.get('sid')
        c_id= request.form.get('cid')
        entry_student_class = Test_student_class(s_id=s_id,class_id=c_id)
        db.session.add(entry_student_class)
        db.session.commit()

    return render_template('assignstudentclass.html')


@app.route("/studentform")
def studentdetails():
    return render_template('studentform.html')


@app.route("/facultyform")
def facultydetails():
    return render_template('FacultyForm.html')

@app.route("/subjectform")
def subjectdetails():
    return render_template('subjectform.html')






app.run(debug=True)
