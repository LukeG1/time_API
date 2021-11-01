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


#TODO: timezones
    



#TODO: Store an acompanying hashmap of user ids to get users in O(1) time? or just switch to a proper database
class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('key', required=True , location="headers", help="API KEY REQUIRED")  # add header
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
        #parser.add_argument('key', required=True , location="headers", help="API KEY REQUIRED")  # add header
        parser.add_argument('name', required=True)  # add args
        parser.add_argument('tz', required=False)  # add args
        args = parser.parse_args()

        users = load_database('users')

        current_user = {
            "id" : users[-1]['id']+1 if len(users)>0 else 0,
            "username" : args['name'],
            "tz" : args['tz'] if args.get('tz') is not None else None, #'tz' in args.keys()
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
        parser.add_argument('key', required=True , location="headers", help="API KEY REQUIRED")  # add header
        parser.add_argument('timer_id', required=False, type=int)  # add args
        parser.add_argument('description', required=False)  # add args
        parser.add_argument('project_id', required=False)  # add args
        parser.add_argument('start', required=False)  # add args
        parser.add_argument('end', required=False)  # add args
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

        running_timer = None
        if(args.get('timer_id') is not None):
            for timer in timers:
                print(timer['id'], int(args['timer_id']), timer['id'] == args['timer_id'])
                if(timer['id'] == args['timer_id']):
                    running_timer = timer
                    break
            print(running_timer)
            if(running_timer == None):
                return {'message': f"'{args['timer_id']}' is an invalid timer id"}, 401


        return_value = None
        if(args['start'] == None and args['end'] == None and args['timer_id'] == None):  # they gave a blank timer
            current_timer = {
                "id" : timers[-1]['id']+1 if len(timers)>0 else 0,
                "user_id" : current_user['id'],
                "description" : args['description'] if args.get('description') is not None else None,
                "start" : datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"),
                "end" : None,
                "project_id" : args['project_id'] if args.get('project_id') is not None else None
            }
            timers.append(current_timer)
            current_user['timers'].append(current_timer['id'])
            return_value = current_timer

        elif(args['timer_id'] is not None and args['end'] is not None and running_timer is not None): # they are ending an exiting timer
            running_timer['end'] = args['end']
            return_value = running_timer

        else: #TODO: check for more valid cases?
            return {'message': "Invalid timer start/end inputs"}, 400

        store_database('timers', timers)
        store_database('users', users)


        #TODO: Alternare forms of timer post: just end timer, both, project_id, etc.

        return {'data': return_value}, 200  # return data and 200 OK code


    #TODO: get for timer in daterange?





class Projects(Resource):
    # methods go here
    pass
    
api.add_resource(Users, '/users')  # '/users' is our entry point for Users
api.add_resource(Timers, '/timers')  # and '/locations' is our entry point for Locations
api.add_resource(Projects, '/projects')  # and '/projects' is our entry point for Projects



if __name__ == '__main__':
    app.run(debug = True)  # run our Flask app