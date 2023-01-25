from flask import Flask, render_template, session, redirect, request
from flask_app import app
from flask_app.models.user import User
from flask_app.models.vehicle import Vehicle
from flask import flash


######## RENDERING GET METHODS ########

@app.route("/vehicles/home")
def vehicles_home():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    vehicles = Vehicle.get_all()


    return render_template("home.html", user=user, vehicles=vehicles)

### If we wanted to have the option to view information of the band, code is below. But it is not on the wireframe. 
@app.route("/vehicles/<int:vehicle_id>")
def vehicle_detail(vehicle_id):
    user = User.get_by_id(session["user_id"])
    vehicle = Vehicle.get_by_id(vehicle_id)
    return render_template("vehicle_detail.html", user=user, vehicle=vehicle)

@app.route("/vehicles/add")
def vehicle_create_page():
    return render_template("add_vehicle.html")


@app.route("/vehicles/edit/<int:vehicle_id>")
def vehicle_edit_page(vehicle_id):
    vehicle = Vehicle.get_by_id(vehicle_id)
    return render_template("edit_vehicle.html", vehicle=vehicle)

@app.route("/myvehicles")
def my_vehicles(user_id):
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    vehicles = Vehicle.get_all(user_id)

    return render_template("my_vehicles.html", user=user, vehicles=vehicles)


######## POST and ACTION METHODS ########

@app.route("/vehicles", methods=["POST"])
def create_vehicle():
    valid_vehicle = Vehicle.create_valid_vehicle(request.form)
    if valid_vehicle:
        return redirect(f'/vehicles/{valid_vehicle.id}')
    return redirect('/vehicles/add')

@app.route("/vehicles/edit/<int:vehicle_id>", methods=["POST"])
def update_vehicle(vehicle_id):
    data = {
        "city": request.form["city"],
        "year": request.form["year"],
        "make": request.form["make"],
        "model": request.form["model"],
        "license": request.form["license"],
        "pickup": request.form["pickup"],
        "dropoff": request.form["dropoff"],
        "phone": request.form["phone"],
        "id": vehicle_id
    }

    valid_vehicle = Vehicle.update_vehicle(data, int(session["user_id"]))

    if not valid_vehicle:
        return redirect(f"/vehicles/edit/{vehicle_id}")
        
    return redirect(f"/vehicles/{vehicle_id}")

@app.route("/vehicles/delete/<int:vehicle_id>")
def delete_by_id(vehicle_id):
    Vehicle.delete_vehicle_by_id(vehicle_id)
    return redirect("/vehicles/home")
