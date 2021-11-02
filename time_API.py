from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json
import ast
import secrets
from datetime import datetime, timezone
from flask_login import UserMixin
from pprint import pprint as pprint

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site002.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#----------------------------------------------------------------------- DATABASE OBJECTS

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    api_key = db.Column(db.String(), nullable=False, unique=True)
    time_zone = db.Column(db.String(), nullable=False, default=0) #ex: EST
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
        }

    def __str__(self):
        return f"USER({self.id},'{self.username}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    color = db.Column(db.String(), nullable=False, default="#292929") #hex color

    time_entries = db.relationship('Time_Entry', backref='project', lazy=True)
    task_entries = db.relationship('Task_Entry', backref='project', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return f"PROJECT({self.id},'{self.name}', '{User.query.get(self.user_id).username}')"

class Time_Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=True)
    start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #iso
    stop = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #iso
    duration = db.Column(db.Integer, nullable=True, default=0) #seconds
    running = db.Column(db.Integer, nullable=False, default=0) #bool (0 or 1)

    #task_id = db.Column(db.Integer, db.ForeignKey('Task_Entry.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return f"TIME_ENTRY({self.id},'{self.description}',{self.duration})"

    def to_dict(self):
        return {
            "id" : self.id,
            "project_id" : self.project_id,
            "user_id" : self.user_id,
            "description" : self.description,
            "running" : self.running,
            "start" : self.start.strftime("%m/%d/%Y, %H:%M:%S"),
            "stop" : self.stop.strftime("%m/%d/%Y, %H:%M:%S"),
        }

class Task_Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), unique=True, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #iso
    do_date = db.Column(db.DateTime, nullable=True) #iso
    priority = db.Column(db.Integer, nullable=False, default=1) #range(1 - 4)
    completed = db.Column(db.Integer, nullable=False, default=0) #bool (0 or 1)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #time_entries = db.relationship('Time_Entry', backref='task_entry', lazy=True)

    def __str__(self):
        return f"TASK_ENTRY({self.id},'{self.description}',{self.due_date})"

# db.drop_all()
# db.create_all()
#------------------------------------------------------------------------------------------ actual website

def load_database(database):
    return json.load(open(f"./json-database/{database}.json","r"))
def store_database(database, value):
    with open(f"./json-database/{database}.json", 'w') as outfile:
        json.dump(value, outfile, indent=4)

def generate_API_key():
    temp_key = secrets.token_urlsafe(16)
    while(len(User.query.filter_by(api_key=temp_key).all()) > 0):
        temp_key = secrets.token_urlsafe(16)

    return temp_key



#TODO: timezones
    


class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('key', required=True , location="headers", help="API KEY REQUIRED")  # add header
        args = parser.parse_args()

        current_user = User.query.filter_by(api_key=args['key']).first()

        if(current_user == None):
            return {'message': f"'{args['key']}' is an invalid API key"}, 401
        return {'data': current_user.to_dict()}, 200  # return data and 200 OK code


    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('username', required=True)  # add args
        parser.add_argument('email', required=True)  # add args
        parser.add_argument('password', required=True)  # add args
        parser.add_argument('tz', required=False)  # add args
        args = parser.parse_args()

        new_user = User(
            api_key = generate_API_key(),
            username = args['username'],
            email = args['email'],
            password = args['password'],
            time_zone = args['tz'] or "UTC",

            admin = 1,
        )
        db.session.add(new_user)
        db.session.commit()

        return {'data': new_user.to_dict()}, 200  # return data and 200 OK code



class Timers(Resource):
    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('key', required=True , location="headers", help="API KEY REQUIRED")  # add header
        parser.add_argument('timer_id', required=False, type=int)  # add args
        parser.add_argument('description', required=False)  # add args
        parser.add_argument('project_id', required=False)  # add args
        parser.add_argument('start', required=False)  # add args
        parser.add_argument('end', required=False)  # add args
        args = parser.parse_args()

        current_user = User.query.filter_by(api_key=args['key']).first()
        if(current_user == None):
            return {'message': f"'{args['key']}' is an invalid API key"}, 401

        running_timer = Time_Entry.query.filter_by(id=args['timer_id'], running=1).first()
        if(args['timer_id'] is not None and running_timer == None):
            return {'message': f"'{args['timer_id']}' is an invalid timer id"}, 401

        return_value = None
        if(args['start'] == None and args['end'] == None and args['timer_id'] == None):  # they gave a blank timer
            if(running_timer is not None):
                return {'message': "You already have a running timer!"}, 401

            new_timer = Time_Entry(
                user_id = current_user.id,
                project_id = args.get('project_id'),
                description = args.get('description'),
                start = datetime.utcnow(), #.strftime("%m/%d/%Y, %H:%M:%S")
                running = 1,
            )
            db.session.add(new_timer)
            db.session.commit()
            return_value = new_timer

        elif(args['timer_id'] is not None and args['end'] is not None and running_timer is not None): # they are ending an exiting timer
            running_timer.stop = args['end']
            running_timer.running = 0
            db.session.commit()
            return_value = running_timer
        
        elif(args['timer_id'] is not None and running_timer is not None):
            running_timer.stop = datetime.utcnow()
            running_timer.running = 0
            db.session.commit()
            return_value = running_timer

        else: #TODO: check for more valid cases?
            return {'message': "Invalid timer start/end inputs"}, 400

        return {'data': return_value.to_dict()}, 200  # return data and 200 OK code


    #TODO: get for timers in date range?
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('key', required=True , location="headers", help="API KEY REQUIRED")  # add header
        parser.add_argument('project_id', required=False)  # add args
        #parser.add_argument('start_date', required=True)  # add args
        #parser.add_argument('end_date', required=True)  # add args
        args = parser.parse_args()
        
        users = load_database('users')
        timers = load_database('timers')

        current_user = None
        for user in users:
            if(user['key'] == args['key']):
                current_user = user
                break
        if(current_user == None):
            return {'message': f"'{args['key']}' is an invalid API key"}, 401
        
        #TODO: start and end dates AFTER PROPER DATABASES
        return_value = []
        for timer in timers:
            if(timer['user_id'] == current_user['id']):
                return_value.append(timer)

        return {'data': return_value}, 200  # return data and 200 OK code



#TODO: tasks as a whole
#       create task
#       get tasks
#       completete task



#TODO: get and post for project completion
class Projects(Resource):
    def post(self):
        pass


    def get(self):
        # if a project id is passed get that one otherwise get all of them
        pass
    


api.add_resource(Users, '/users')  # '/users' is our entry point for Users
api.add_resource(Timers, '/timers')  # and '/locations' is our entry point for Locations
api.add_resource(Projects, '/projects')  # and '/projects' is our entry point for Projects



if __name__ == '__main__':
    app.run(debug = True)  # run our Flask app
