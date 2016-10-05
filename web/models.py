
""" models.py - Provide database model"""
from datetime import datetime
from views import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User {0}>'.format(self.name)


class Model(db.Model):

   __tablename__ = "models"

   id = db.Column(db.Integer, primary_key=True)
   exp_name = db.Column(db.String, nullable=False)
   time_simulation = db.Column(db.Integer, nullable=False)
   time_simulation_unit = db.Column(db.String, nullable=False)
   #integration_time = db.Column(db.Integer, nullable=False)
   initial_date = db.Column(db.Date, default=datetime.utcnow())
   initial_hour_hour = db.Column(db.Integer, nullable=False)
   initial_hour_minute = db.Column(db.Integer, nullable=False)
   center_point_latitude = db.Column(db.Float, nullable=False)
   center_point_longitude = db.Column(db.Float, nullable=False)
   number_points_x_y = db.Column(db.Integer, nullable=False)
   distance_x_y = db.Column(db.Integer, nullable=False)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'))



   def __init__(self, exp_name, time_simulation, time_simulation_unit, initial_date,
               initial_hour_hour, initial_hour_minute, center_point_latitude, center_point_longitude, number_points_x_y, distance_x_y, user_id):
       self.exp_name = exp_name
       self.time_simulation = time_simulation
       self.time_simulation_unit = time_simulation_unit
       #self.integration_time = integration_time
       self.initial_date = initial_date
       self.initial_hour_hour = initial_hour_hour
       self.initial_hour_minute = initial_hour_minute
       self.center_point_latitude = center_point_latitude
       self.center_point_longitude = center_point_longitude
       self.number_points_x_y = number_points_x_y
       self.distance_x_y = distance_x_y
       self.user_id = user_id

   def __repr__(self):
       return '<Model {0}>'.format(self.exp_name)
