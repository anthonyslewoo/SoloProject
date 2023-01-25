# import the function that will return an instance of a connection
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
from flask_app.models import user
import re

db = "soloproject"

class Vehicle:
    def __init__(self, vehicle):
        self.id = vehicle["id"]
        self.city = vehicle["city"]
        self.year = vehicle["year"]
        self.make = vehicle["make"]
        self.model = vehicle["model"]
        self.license = vehicle["license"]
        self.pickup = vehicle["pickup"]
        self.dropoff = vehicle["dropoff"]
        self.phone = vehicle["phone"]
        self.created_at = vehicle["created_at"]
        self.updated_at = vehicle["updated_at"]
        self.user_id = vehicle["user_id"]

    @classmethod
    def create_valid_vehicle(cls, vehicle_dict):
        if not cls.is_valid(vehicle_dict):
            return False

        query = """INSERT INTO vehicles (city, year, make, model, license, pickup, dropoff, phone, user_id) 
        VALUES (%(city)s, %(year)s, %(make)s, %(model)s, %(license)s, %(pickup)s, %(dropoff)s, %(phone)s, %(user_id)s);"""
        vehicle_id = connectToMySQL(db).query_db(query, vehicle_dict)
        vehicle = cls.get_by_id(vehicle_id)

        return vehicle


    @classmethod
    def get_by_id(cls, vehicle_id):
        print(f"get vehicle by id {vehicle_id}")
        data = {"id": vehicle_id}
        query = """SELECT vehicles.id, vehicles.created_at, vehicles.updated_at, 
                city, year, make, model, license, pickup, dropoff, phone, users.id as user_id, first_name, last_name, email, password,
                users.created_at as uc, users.updated_at as uu
                FROM vehicles
                JOIN users on users.id = vehicles.user_id
                WHERE vehicles.id = %(id)s;"""

        result = connectToMySQL(db).query_db(query, data)
        print("result of query:")
        print(result)
        result = result[0]
        vehicle = cls(result)

        ### converts user data into a user object
        vehicle.user = user.User(
            {
                "id": result["user_id"],
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "email": result["email"],
                "password": result["password"],
                "created_at": result["uc"],
                "updated_at": result["uu"]
            }
        )

        return vehicle

    @classmethod
    def delete_vehicle_by_id(cls, vehicle_id):
        data = {"id": vehicle_id}
        query = "DELETE from vehicles WHERE id = %(id)s;"
        connectToMySQL(db).query_db(query, data)

        return vehicle_id

    ### may not use this method but here in case it is implemented....

    @classmethod
    def update_vehicle(cls, vehicle_dict, session_id):
        ## authentice user
        vehicle = cls.get_by_id(vehicle_dict["id"])
        if vehicle.user_id != session_id:
            flash("You must be the owner of this vehicle to update transport")
            return False

        ## validates input
        if not cls.is_valid(vehicle_dict):
            return False

        ## updates the data in db
        query = """UPDATE vehicles SET city = %(city)s, year = %(year)s, make = %(make)s, model = %(model)s,
                license = %(license)s, pickup = %(pickup)s, dropoff = %(dropoff)s, phone = %(phone)s WHERE id = %(id)s;"""

        result = connectToMySQL(db).query_db(query, vehicle_dict)
        vehicle = cls.get_by_id(vehicle_dict["id"])
        return vehicle


    @classmethod
    def get_all(cls):
        ### get all vehicles and user info 
        query = """SELECT
                    vehicles.id, vehicles.created_at, vehicles.updated_at, city, year, make, model, license, pickup, dropoff, phone,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM vehicles
                    JOIN users on users.id = vehicles.user_id"""

        vehicle_data = connectToMySQL(db).query_db(query)

        ## make a list to hold vehicles
        vehicles = []

        for vehicle in vehicle_data:
            vehicle_obj = cls(vehicle)

            vehicle_obj.user = user.User(
                {
                    "id": vehicle["user_id"],
                    "first_name": vehicle["first_name"],
                    "last_name": vehicle["last_name"],
                    "email": vehicle["email"],
                    "password": vehicle["password"],
                    "created_at": vehicle["uc"],
                    "updated_at": vehicle["uu"]

                }
            )    
            vehicles.append(vehicle_obj)

        return vehicles


    @staticmethod
    def is_valid(vehicle_dict):
        valid = True
        flash_string = " field is required and must be atleast 2 characters."
        if len(vehicle_dict["city"]) < 2:
            flash("City" + flash_string)
            valid = False
        # if  vehicle_dict["year"] < 1900:
        #    flash("Vehicle year must by newer than a 1900.")
        #   valid = False
        if len(vehicle_dict["make"]) < 2:
            flash("Vehicle make" + flash_string)
            valid = False
        if len(vehicle_dict["model"]) < 2:
            flash("Vehicle model" + flash_string)
            valid = False
        if len(vehicle_dict["license"]) < 2:
            flash("Vehicle license" + flash_string)
            valid = False
        if len(vehicle_dict["pickup"]) < 2:
            flash("Pick up address should have no commas, street # city and state")
            valid = False
        if len(vehicle_dict["dropoff"]) < 2:
            flash("drop off address should have no commas, street # city and state")
            valid = False
        if len(vehicle_dict["phone"]) <= 9:
            flash("phone number should be alteast 10 numbers.")
            valid = False
        if len(vehicle_dict["phone"]) >= 11:
            flash("phone number should be only 10 numbers.")
            valid = False
        
        return valid






