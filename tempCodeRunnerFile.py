from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json
import ast
import secrets
from datetime import datetime, timedelta, timezone
import pytz
from flask_login import UserMixin
from pprint import pprint as pprint

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site005.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#----------------------------------------------------------------------- DATABASE OBJECTS

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    api_key = db.Column(db.String(), nullable=False, unique=True)
    time_zone = db.Column(db.String(), nullable=False, default=0) #ex: US/Eastern
    admin = db.Column(db.Integer, nullable=False, default=0) #bool (0 or 1)

    projects = db.relationship('Project', backref='user', lazy=True)
    task_entries = db.relationship('Task_Entry', backref='user', lazy=True)
    time_entries = db.relationship('Time_Entry', backref='user', lazy=True)

    def to_dict(self):
        return {
            "id" : self.id,
            "username" : self.username,
            "email" : self.email,
            "password" : self.password,
            "api_key" : self.api_key,
            "time_zone" : self.time_zone,
            "admin" : self.admin,
            "time_entries" : list(map(str, self.time_entries))  #TODO: Delete this, will get too big to display to the user
        }

    def __str__(self):
        return f"USER({self.id},'{self.username}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    color = db.Column(db.String(), nullable=False, default="#292929") #hex color
    active = db.Column(db.Integer, nullable=False, default=1) #bool (0 or 1)

    time_entries = db.relationship('Time_Entry', backref='project', lazy=True)
    task_entries = db.relationship('Task_Entry', backref='project', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return f"PROJECT({self.id},'{self.name}', '{User.query.get(self.user_id).username}')"

class Task_Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), unique=True, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #iso
    do_date = db.Column(db.DateTime, nullable=True) #iso
    priority = db.Column(db.Integer, nullable=False, default=1) #range(1 - 4)
    completed = db.Column(db.Integer, nullable=False, default=0) #bool (0 or 1)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_entries = db.relationship('Time_Entry', backref='task_entry', lazy=True)

    def __str__(self):
        return f"TASK_ENTRY({self.id},'{self.description}',{self.due_date})"

class Time_Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=True)
    start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #iso
    stop = db.Column(db.DateTime, nullable=True) #iso
    duration = db.Column(db.Integer, nullable=True, default=0) #seconds
    running = db.Column(db.Integer, nullable=False, default=0) #bool (0 or 1)

    #TODO: link to tasks
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_entry_id = db.Column(db.Integer, db.ForeignKey('Task_Entry.id'), nullable=True)

    def __str__(self):
        return f"TIME_ENTRY({self.id},'{self.description}',{self.duration})"

    def to_dict(self):
        tz = pytz.timezone(User.query.get(self.user_id).time_zone) # US/Eastern  #.replace(tzinfo=pytz.utc).astimezone(tz)
        stop_display = self.stop or datetime.utcnow()
        return {
            "id" : self.id,
            "project_id" : self.project_id,
            "user_id" : self.user_id,
            "description" : self.description,
            "running" : self.running,
            "start" : self.start.replace(tzinfo=pytz.utc).astimezone(tz).strftime("%m/%d/%Y, %H:%M:%S"),
            "stop" : stop_display.replace(tzinfo=pytz.utc).astimezone(tz).strftime("%m/%d/%Y, %H:%M:%S"),
        }

db.drop_all()
db.create_all()