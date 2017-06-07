from flask import Flask, render_template, session, sessions, redirect, url_for, request, flash
from flask_login import LoginManager
from flask_login import login_user , logout_user , current_user , login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import statistics
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import MySQLdb
from plotly.graph_objs import *
import plotly.tools as tls
import plotly.dashboard_objs as dashboard
from sqlalchemy.types import String
from sqlalchemy import create_engine

conn = MySQLdb.connect(host="mysql.agh.edu.pl", user="uzuch", passwd="e1eSLKm9Y1NTMt27", db="uzuch")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://uzuch:e1eSLKm9Y1NTMt27@mysql.agh.edu.pl/uzuch'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

engine = create_engine('mysql://uzuch:e1eSLKm9Y1NTMt27@mysql.agh.edu.pl/uzuch')

class Questdata(db.Model):
    __tablename__ = 'questdata'
    quest_id = db.Column(db.Integer, primary_key=True, unique=True)
    sex = db.Column(db.String(10))
    faculty = db.Column(db.String(150))
    field = db.Column(db.String(150))
    degree = db.Column(db.String(2))
    degree_value = db.Column(db.String(20))
    work_skill = db.Column(db.String(10))
    skill_req = db.Column(db.String(10))
    meet_req = db.Column(db.String(10))
    self_develop = db.Column(db.String(10))
    job = db.Column(db.String(10))
    recommend = db.Column(db.String(10))

    def __init__(self, quest_id, sex, faculty, field, degree, degree_value, work_skill, skill_req, meet_req, self_develop, job, recommend):
        self.quest_id = quest_id
        self.sex = sex
        self.faculty = faculty
        self.field = field
        self.degree = degree
        self.degree_value = degree_value
        self.work_skill = work_skill
        self.skill_req = skill_req
        self.meet_req = meet_req
        self.self_develop = self_develop
        self.job = job
        self.recommend = recommend

db.create_all()

@login_manager.user_loader
def load_user(quest_id):
    return Questdata.get(quest_id)

login_manager.login_view = 'quest_id'

def is_authenticated(self):
    return True

def is_active(self):
    return True

def is_anonymous(self):
    return False

def get_id(self):
    return unicode(self.quest_id)

def __repr__(self):
    return '<User %r>' % (self.quest_id)

@app.route("/")
def welcome():
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        quest_id = request.form['quest_id']
        password = request.form['password']
        registered_user = Questdata.query.filter_by(quest_id=quest_id,password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('login'))
        login_user(registered_user)
        flash('Logged in successfully')
    return render_template('login.html')

@app.route("/questionnaire")
def show_patient():
    fd = db.session.query(Questdata).all()

    return render_template('questionnaire.html', formdata=fd)

@app.route("/archiwum")
def archiwum():
    fd = db.session.query(Questdata).all()
    return render_template('archiwum.html', formdata=fd)




@app.route("/new_survey")
def show_result():
    fd_list = db.session.query(Questdata).all()



    # Prepare data for google charts
    #data = [['Satisfaction', mean_satisfaction], ['Python skill', mean_q1], ['Flask skill', mean_q2]]

    return render_template('new_survey.html', data=fd_list)


@app.route("/save", methods=['POST'])
def save():
    # Get data from FORM
    quest_id = request.form['quest_id']
    sex=request.form['sex']
    faculty = request.form['faculty']
    field = request.form['field']
    degree = request.form['degree']
    degree_value = request.form['degree_value']
    work_skill = request.form['work_skill']
    skill_req = request.form['skill_req']
    meet_req = request.form['meet_req']
    self_develop = request.form['self_develop']
    job = request.form['job']
    recommend = request.form['recommend']

    # Save the data
    fd = Questdata(quest_id, sex, faculty, field, degree, degree_value, work_skill, skill_req, meet_req, self_develop, job, recommend)
    db.session.add(fd)
    db.session.commit()

    return redirect('/')

@app.route("/load")
def load():
    with engine.connect() as conn, conn.begin():
        data = pd.read_sql_table('questdata', conn)

    return render_template('load_survey.html', data=data)


if __name__ == "__main__":
    app.secret_key = 'some secret key'
    app.debug = True
    app.run()