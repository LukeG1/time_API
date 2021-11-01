from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import json
import ast
import secrets
from datetime import datetime

app = Flask(__name__)
api = Api(app)

from pprint import pprint as pprint




def load_database(database):
    return json.load(open(f"./json-database/{database}.json","r"))
def store_database(database, value):
    with open(f"./json-database/{database}.json", 'w') as outfile:
        json.dump(value, outfile, indent=4)

def generate_API_key(existing_users):
    current_keys = []
    for user in existing_users:
        current_keys.append(user['key'])

    temp_key = secrets.token_urlsafe(16)
    while(temp_key in current_keys):
        temp_key = secrets.token_urlsafe(16)

    return temp_key
    



#TODO: Store an acompanying hashmap of user ids to get users in O(1) time? or just switch to a proper database
class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('key', required=True)  # add args
        args = parser.parse_args()

        users = load_database('users')

        current_user = None
        for user in users:
            if(user['key'] == args['key']):
                current_user = user
                break

        if(current_user == None):
            return {'message': f"'{args['key']}' is an invalid API key"}, 401
        return {'data': current_user}, 200  # return data and 200 OK code


    def post(self):
        #TODO: adds a new user and returns them so that the api key can be saved by the sender
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('name', required=True)  # add args
        args = parser.parse_args()

        users = load_database('users')

        temp_id = 0
        if(len(users) > 0):
            temp_id = users[-1]['id'] + 1

        current_user = {
            "id" : temp_id,
            "username" : args['name'],
            "key" : generate_API_key(users),
            "timers" : [],
            "projects" : [],
        }
        users.append(current_user)

        store_database('users', users)

        return {'data': current_user}, 200  # return data and 200 OK code






class Timers(Resource):
    # methods go here
    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('timer_id', required=False)  # add args
        parser.add_argument('key', required=True)  # add args
        parser.add_argument('description', required=False)  # add args
        parser.add_argument('project_id', required=False)  # add args
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

        temp_id = 0
        if(len(timers) > 0):
            temp_id = users[-1]['id'] + 1

        current_timer = {
            "id" : temp_id,
            "user_id" : current_user['id'],
            "description" : args['description'],
            "start" : datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"),
            "end" : None,
            "project_id" : 0
        }
        timers.append(current_timer)

        current_user['timers'].append(current_timer['id'])

        store_database('timers', timers)
        store_database('users', users)


        #TODO: Alternare forms of timer post: just end timer, both, project_id, etc.

        return {'data': current_timer}, 200  # return data and 200 OK code






class Projects(Resource):
    # methods go here
    pass
    
api.add_resource(Users, '/users')  # '/users' is our entry point for Users
api.add_resource(Timers, '/timers')  # and '/locations' is our entry point for Locations
api.add_resource(Projects, '/projects')  # and '/projects' is our entry point for Projects



if __name__ == '__main__':
    app.run(debug = True)  # run our Flask app