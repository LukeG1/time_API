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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site003.db'
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
            "time_entries" : list(map(str, self.time_entries))  #TODO: Delete this, will get too big to display to the user
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
    #TODO: archived attribute (could invert to active)

    def __str__(self):
        return f"PROJECT({self.id},'{self.name}', '{User.query.get(self.user_id).username}')"

class Time_Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=True)
    start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #iso
    stop = db.Column(db.DateTime, nullable=True) #iso
    duration = db.Column(db.Integer, nullable=True, default=0) #seconds
    running = db.Column(db.Integer, nullable=False, default=0) #bool (0 or 1)

    #TODO: link to tasks
    #task_id = db.Column(db.Integer, db.ForeignKey('Task_Entry.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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



#TODO: DOCUMENTATION, I will forget how all this works eventually, probably make a readme


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


#TODO: this is stated in other places but I need to deal with how I want to recieve datetimes, probably iso string
class Timers(Resource):
    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('key', required=True , location="headers", help="API KEY REQUIRED")  # add header
        parser.add_argument('time_entry_id', required=False, type=int)  # add args
        parser.add_argument('description', required=False)  # add args
        parser.add_argument('project_id', required=False)  # add args
        parser.add_argument('start', required=False)  # add args
        parser.add_argument('end', required=False)  # add args
        args = parser.parse_args()

        current_user = User.query.filter_by(api_key=args['key']).first()
        if(current_user == None):
            return {'message': f"'{args['key']}' is an invalid API key"}, 401

        running_timer = Time_Entry.query.filter_by(id=args['time_entry_id'], running=1).first()
        if(args['time_entry_id'] is not None and running_timer == None):
            return {'message': f"'{args['time_entry_id']}' is an invalid timer id"}, 401

        return_value = None
        if(args['start'] == None and args['end'] == None and args['time_entry_id'] == None):  # they gave a blank timer
            if(Time_Entry.query.filter_by(running=1).first() is not None):
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

        #TODO: This case is dumb, replace it with a manual time entry, deal with mods later
        elif(args['time_entry_id'] is not None and args['end'] is not None and running_timer is not None): # they are ending an exiting timer
            running_timer.stop = args['end']
            running_timer.running = 0
            db.session.commit()
            return_value = running_timer
        
        elif(args['time_entry_id'] is not None and running_timer is not None):
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
        parser.add_argument('mode', required=False)
        parser.add_argument('start_time', required=False)  # add args
        parser.add_argument('stop_time', required=False)  # add args
        args = parser.parse_args()

        current_user = User.query.filter_by(api_key=args['key']).first()
        if(current_user == None):
            return {'message': f"'{args['key']}' is an invalid API key"}, 401

        return_value = None
        if(args.get('mode') == None or args.get('mode') == '0'): #default, return the running timer or nothing
            timer = Time_Entry.query.filter_by(user_id=current_user.id, running=1).first()
            if(timer is not None):
                return_value = timer.to_dict()

        elif(args.get('mode') == '1'): # since the start time 
            try:
                if(type(args.get('start_time')) == str):
                    if(", " in args.get('start_time')):
                        start_time = datetime.strptime(args.get('start_time'), "%m/%d/%Y, %H:%M:%S")
                    else:
                        start_time = datetime.strptime(args.get('start_time'), "%m/%d/%Y")
                else:
                    return {'message': "Invalid datetime format"}, 400
            except ValueError:
                return {'message': "Invalid datetime format"}, 400
            return_value = Time_Entry.query.filter(
                Time_Entry.user_id == current_user.id, 
                Time_Entry.start >= start_time, 
            ).all()
            return_value = list(map(Time_Entry.to_dict, return_value))

        elif(args.get('mode') == '2'): # between the start and end times
            try:
                if(type(args.get('start_time')) == str):
                    if(", " in args.get('start_time')):
                        start_time = datetime.strptime(args.get('start_time'), "%m/%d/%Y, %H:%M:%S")
                    else:
                        start_time = datetime.strptime(args.get('start_time'), "%m/%d/%Y")
                else:
                    return {'message': "Invalid datetime format"}, 400
            except ValueError:
                return {'message': "Invalid datetime format"}, 400
            try:
                if(type(args.get('stop_time')) == str):
                    if(", " in args.get('stop_time')):
                        stop_time = datetime.strptime(args.get('stop_time'), "%m/%d/%Y, %H:%M:%S")
                    else:
                        stop_time = datetime.strptime(args.get('stop_time'), "%m/%d/%Y")
                        stop_time += timedelta(hours=23, minutes=59, seconds=59)
                else:
                    return {'message': "Invalid datetime format"}, 400
            except ValueError:
                return {'message': "Invalid datetime format"}, 400

            return_value = Time_Entry.query.filter(
                Time_Entry.user_id == current_user.id, 
                Time_Entry.start >= start_time, 
                Time_Entry.stop <= stop_time
            ).all()
            return_value = list(map(Time_Entry.to_dict, return_value))

        elif(args.get('mode') == '3'): # everything
            return_value = Time_Entry.query.filter_by(user_id=current_user.id).all()
            return_value = list(map(Time_Entry.to_dict, return_value))

        return {'data': return_value}, 200  # return data and 200 OK code



#TODO: tasks as a whole
class Tasks(Resource):
    def post(self):
        pass

    def get(self):
        pass



#TODO: get and post for project creation
class Projects(Resource):
    def post(self):
        pass

    def get(self):
        # if a project id is passed get that one otherwise get all of them
        pass
    


api.add_resource(Users, '/users')  # '/users' is our entry point for Users
api.add_resource(Projects, '/projects')  # and '/projects' is our entry point for Projects
api.add_resource(Tasks, '/task_entries')  # and '/tasks' is our entry point for Tasks
api.add_resource(Timers, '/time_entries')  # and '/locations' is our entry point for Locations



if __name__ == '__main__':
    app.run(debug = True)  # run our Flask app



common_timezones = ['Africa/Abidjan', 'Africa/Accra', 'Africa/Addis_Ababa', 'Africa/Algiers', 'Africa/Asmara', 'Africa/Bamako', 'Africa/Bangui', 'Africa/Banjul', 'Africa/Bissau', 'Africa/Blantyre', 'Africa/Brazzaville', 'Africa/Bujumbura', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Ceuta', 'Africa/Conakry', 'Africa/Dakar', 'Africa/Dar_es_Salaam', 'Africa/Djibouti', 'Africa/Douala', 'Africa/El_Aaiun', 'Africa/Freetown', 'Africa/Gaborone', 'Africa/Harare', 'Africa/Johannesburg', 'Africa/Juba', 'Africa/Kampala', 'Africa/Khartoum', 'Africa/Kigali', 'Africa/Kinshasa', 'Africa/Lagos', 'Africa/Libreville', 'Africa/Lome', 'Africa/Luanda', 'Africa/Lubumbashi', 'Africa/Lusaka', 'Africa/Malabo', 'Africa/Maputo', 'Africa/Maseru', 'Africa/Mbabane', 'Africa/Mogadishu', 'Africa/Monrovia', 'Africa/Nairobi', 'Africa/Ndjamena', 'Africa/Niamey', 'Africa/Nouakchott', 'Africa/Ouagadougou', 'Africa/Porto-Novo', 'Africa/Sao_Tome', 'Africa/Tripoli', 'Africa/Tunis', 'Africa/Windhoek', 'America/Adak', 'America/Anchorage', 'America/Anguilla', 'America/Antigua', 'America/Araguaina', 'America/Argentina/Buenos_Aires', 'America/Argentina/Catamarca', 'America/Argentina/Cordoba', 'America/Argentina/Jujuy', 'America/Argentina/La_Rioja', 'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos', 'America/Argentina/Salta', 'America/Argentina/San_Juan', 'America/Argentina/San_Luis', 'America/Argentina/Tucuman', 'America/Argentina/Ushuaia', 'America/Aruba', 'America/Asuncion', 'America/Atikokan', 'America/Bahia', 'America/Bahia_Banderas', 'America/Barbados', 'America/Belem', 'America/Belize', 'America/Blanc-Sablon', 'America/Boa_Vista', 'America/Bogota', 'America/Boise', 'America/Cambridge_Bay', 'America/Campo_Grande', 'America/Cancun', 'America/Caracas', 'America/Cayenne', 'America/Cayman', 'America/Chicago', 'America/Chihuahua', 'America/Costa_Rica', 'America/Creston', 'America/Cuiaba', 'America/Curacao', 'America/Danmarkshavn', 'America/Dawson', 'America/Dawson_Creek', 'America/Denver', 'America/Detroit', 'America/Dominica', 'America/Edmonton', 'America/Eirunepe', 'America/El_Salvador', 'America/Fort_Nelson', 'America/Fortaleza', 'America/Glace_Bay', 'America/Godthab', 'America/Goose_Bay', 'America/Grand_Turk', 'America/Grenada', 'America/Guadeloupe', 'America/Guatemala', 'America/Guayaquil', 'America/Guyana', 'America/Halifax', 'America/Havana', 'America/Hermosillo', 'America/Indiana/Indianapolis', 'America/Indiana/Knox', 'America/Indiana/Marengo', 'America/Indiana/Petersburg', 'America/Indiana/Tell_City', 'America/Indiana/Vevay', 'America/Indiana/Vincennes', 'America/Indiana/Winamac', 'America/Inuvik', 'America/Iqaluit', 'America/Jamaica', 'America/Juneau', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Kralendijk', 'America/La_Paz', 'America/Lima', 'America/Los_Angeles', 'America/Lower_Princes', 'America/Maceio', 'America/Managua', 'America/Manaus', 'America/Marigot', 'America/Martinique', 'America/Matamoros', 'America/Mazatlan', 'America/Menominee', 'America/Merida', 'America/Metlakatla', 'America/Mexico_City', 'America/Miquelon', 'America/Moncton', 'America/Monterrey', 'America/Montevideo', 'America/Montserrat', 'America/Nassau', 'America/New_York', 'America/Nipigon', 'America/Nome', 'America/Noronha', 'America/North_Dakota/Beulah', 'America/North_Dakota/Center', 'America/North_Dakota/New_Salem', 'America/Ojinaga', 'America/Panama', 'America/Pangnirtung', 'America/Paramaribo', 'America/Phoenix', 'America/Port-au-Prince', 'America/Port_of_Spain', 'America/Porto_Velho', 'America/Puerto_Rico', 'America/Punta_Arenas', 'America/Rainy_River', 'America/Rankin_Inlet', 'America/Recife', 'America/Regina', 'America/Resolute', 'America/Rio_Branco', 'America/Santarem', 'America/Santiago', 'America/Santo_Domingo', 'America/Sao_Paulo', 'America/Scoresbysund', 'America/Sitka', 'America/St_Barthelemy', 'America/St_Johns', 'America/St_Kitts', 'America/St_Lucia', 'America/St_Thomas', 'America/St_Vincent', 'America/Swift_Current', 'America/Tegucigalpa', 'America/Thule', 'America/Thunder_Bay', 'America/Tijuana', 'America/Toronto', 'America/Tortola', 'America/Vancouver', 'America/Whitehorse', 'America/Winnipeg', 'America/Yakutat', 'America/Yellowknife', 'Antarctica/Casey', 'Antarctica/Davis', 'Antarctica/DumontDUrville', 'Antarctica/Macquarie', 
'Antarctica/Mawson', 'Antarctica/McMurdo', 'Antarctica/Palmer', 'Antarctica/Rothera', 'Antarctica/Syowa', 'Antarctica/Troll', 'Antarctica/Vostok', 'Arctic/Longyearbyen', 'Asia/Aden', 'Asia/Almaty', 'Asia/Amman', 'Asia/Anadyr', 'Asia/Aqtau', 'Asia/Aqtobe', 'Asia/Ashgabat', 'Asia/Atyrau', 'Asia/Baghdad', 'Asia/Bahrain', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Barnaul', 'Asia/Beirut', 'Asia/Bishkek', 'Asia/Brunei', 'Asia/Chita', 'Asia/Choibalsan', 'Asia/Colombo', 'Asia/Damascus', 'Asia/Dhaka', 'Asia/Dili', 'Asia/Dubai', 'Asia/Dushanbe', 'Asia/Famagusta', 'Asia/Gaza', 'Asia/Hebron', 'Asia/Ho_Chi_Minh', 'Asia/Hong_Kong', 'Asia/Hovd', 'Asia/Irkutsk', 'Asia/Jakarta', 'Asia/Jayapura', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Kathmandu', 
'Asia/Khandyga', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur', 'Asia/Kuching', 'Asia/Kuwait', 'Asia/Macau', 'Asia/Magadan', 'Asia/Makassar', 'Asia/Manila', 'Asia/Muscat', 'Asia/Nicosia', 'Asia/Novokuznetsk', 'Asia/Novosibirsk', 'Asia/Omsk', 'Asia/Oral', 'Asia/Phnom_Penh', 'Asia/Pontianak', 'Asia/Pyongyang', 'Asia/Qatar', 'Asia/Qostanay', 'Asia/Qyzylorda', 'Asia/Riyadh', 'Asia/Sakhalin', 'Asia/Samarkand', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Thimphu', 'Asia/Tokyo', 'Asia/Tomsk', 'Asia/Ulaanbaat/Azores', 'Atlantic/Bermuda', 'Atlantic/Canary', 'Atlantic/Cape_Verde', 'Atlantic/Faroe', 'Atlantic/Madeira', 'Atlantic/Reykjavik', 'Atlantic/South_Georgia', 'Atlantic/St_Helena', 'Atlantic/Stanley', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Broken_Hill', 'Australia/Currie', 'Australia/Darwin', 'Australia/Eucla', 'Australia/Hobart', 'Australia/Lindeman', 'Australia/Lord_Howe', 'Australia/Melbourne', 'Australia/Perth', 'Australia/Sydney', 'Canada/Atlantic', 'Canada/Central', 'Canada/Eastern', 'Canada/Mountain', 'Canada/Newfoundland', 'Canada/Pacific', 'Europe/Amsterdam', 'Europe/Andorra', 'Europe/Astrakhan', 'Europe/Athens', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Busingen', 'Europe/Chisinau', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Gibraltar', 'Europe/Guernsey', 'Europe/Helsinki', 'Europe/Isle_of_Man', 'Europe/Istanbul', 'Europe/Jersey', 'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Kirov', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/Luxembourg', 'Europe/Madrid', 'Europe/Malta', 'Europe/Mariehamn', 'Europe/Minsk', 'Europe/Monaco', 'Europe/Moscow', 'Europe/Oslo', 'Europe/Paris', 'Europe/Podgorica', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/San_Marino', 'Europe/Sarajevo', 'Europe/Saratov', 'Europe/Simferopol', 
'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Tirane', 'Europe/Ulyanovsk', 'Europe/Uzhgorod', 'Europe/Vaduz', 'Europe/Vatican', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Europe/Zaporozhye', 'Europe/Zurich', 'GMT', 'Indian/Antananarivo', 'Indian/Chagos', 'Indian/Christmas', 'Indian/Cocos', 'Indian/Comoro', 'Indian/Kerguelen', 'Indian/Mahe', 'Indian/Maldives', 'Indian/Mauritius', 'Indian/Mayotte', 'Indian/Reunion', 'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Bougainville', 'Pacific/Chatham', 'Pacific/Chuuk', 'Pacific/Easter', 
'Pacific/Efate', 'Pacific/Enderbury', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Funafuti', 'Pacific/Galapagos', 'Pacific/Gambier', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu', 'Pacific/Kiritimati', 'Pacific/Kosrae', 'Pacific/Kwajalein', 'Pacific/Majuro', 'Pacific/Marquesas', 'Pacific/Midway', 'Pacific/Nauru', 'Pacific/Niue', 'Pacific/Norfolk', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Palau', 'Pacific/Pitcairn', 'Pacific/Pohnpei', 'Pacific/Port_Moresby', 'Pacific/Rarotonga', 'Pacific/Saipan', 'Pacific/Tahiti', 'Pacific/Tarawa', 'Pacific/Tongatapu', 'Pacific/Wake', 'Pacific/Wallis', 'US/Alaska', 'US/Arizona', 'US/Central', 'US/Eastern', 'US/Hawaii', 'US/Mountain', 'US/Pacific', 'UTC']