"""
This file contains web APIs for an on call cab service.
Using these APIs we can see the list of cabs availabe in google map.
We can book a nearest cab and also can end the trip and get the amount consumer need to pay.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from cab.models import Cabs
from geopy import distance
from geopy import Point
import json

# --------------------- Index view -------------------------
@csrf_protect
def index(request):
    """
    This method will be called initially when we open the application first time
    and also with the post request to book the cab.
    """
    response = {}
    if request.POST:
        car_number = request.POST['car_number']
        lat = request.POST['lat']
        lng = request.POST['lng']
        cab = Cabs.objects.get(cab_number = car_number)
        car_name = cab.car_name
        cab.car_booked = True
        cab.lat = lat
        cab.lng = lng
        cab.save()
        response['car_number'] = car_number
        response['car_name'] = car_name
    cabs = Cabs.objects.values()
    response['cabs'] = cabs
    print response
    return render(request, 'index.html', response)
    
    
# --------------------- Get Cars view ---------------------------------------
def get_cars(request):
    """
    This method is used to get the number of cars available near the provided
    location with kilometer range.
    """
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    km_range = request.GET.get('km_range')
    car_choice = request.GET.get('car_choice')
    db_cars = []
    if car_choice == 'pink':
        db_cars = Cabs.objects.filter(car_booked=False, car_pink=True).values('cab_number', 'latitude', 'longitude')
    else:
        db_cars = Cabs.objects.filter(car_booked=False).values('cab_number', 'latitude', 'longitude')
    cars_in_range = 0
    nearest_car = {}
    min_dist = km_range
    user_loc = Point(str(lat) + ", "+ str(lng))
    for car in db_cars:
        car_loc = Point(str(car['latitude']) + ", " + str(car['longitude']))
        dist = distance.distance(user_loc, car_loc).kilometers
        if dist <= int(km_range):
            cars_in_range += 1
            if dist < min_dist:
                nearest_car = car
    to_json = {}
    to_json['cars_available'] = cars_in_range
    to_json['nearest_car'] = nearest_car
    return HttpResponse(json.dumps(to_json), content_type="application/json")

    
# --------------------- Manage Trip view ------------------------------------   
def manage_trip(request):
    return render(request, 'manage_trip.html')
 
# --------------------- End Trip view ---------------------------------------   
def end_trip(request):
    """
    This method is used to end the trip and get the total amount consumer need
    to pay and also the breakdown of all charges.
    """
    per_minute_price = 1
    per_km_price = 2
    pink_extra_cost = 5
    GST = 14.5
    
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    minutes = request.GET.get('minutes')
    car_number = request.GET.get('car_number')
    
    db_cab = Cabs.objects.get(cab_number = car_number)
    start_lat = db_cab.latitude
    start_lng = db_cab.longitude
    car_pink = db_cab.car_pink
    
    db_cab.latitude = lat
    db_cab.longitude = lng
    db_cab.car_booked = False
    db_cab.save()
    
    start_point = Point(str(start_lat) + ", " + str(start_lng))
    end_point = Point(str(lat) + ", " + str(lng))
    dist = distance.distance(start_point, end_point).kilometers
    km_charge = float(dist) * per_km_price
    time_charge = int(minutes) * per_minute_price
    extra_charge = 0
    if car_pink:
        extra_charge = pink_extra_cost
    total_amount = km_charge + time_charge + extra_charge
    tax = total_amount * (GST/100)
    final_amount = total_amount + tax
    to_json = {}
    to_json['distance'] = round(dist, 2)
    to_json['km_charge'] = round(km_charge, 2)
    to_json['minutes_charge'] = round(time_charge, 2)
    to_json['extra_charge'] = extra_charge
    to_json['gst'] = round(tax, 2)
    to_json['final_amount'] = round(final_amount, 2)
    return HttpResponse(json.dumps(to_json), content_type="application/json")
    
