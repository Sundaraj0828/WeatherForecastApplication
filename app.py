from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session  # type: ignore
import requests
import random
import datetime as dt

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = b'w3@+43rf0r<@&+@997!<@+!09'

# Initialize Flask-Session
sess = Session()
sess.init_app(app)
# --------------------------Acu Weather 
API_KEY = 'sECRETkEY_123456798'

# ----------------------------------------placeholders : 1 = location key, 2 = api key--------------------------------------------- 
BASE_FORECAST_URL = 'http://dataservice.accuweather.com/currentconditions/v1/{}?apikey={}&language=en-in&details=true'
# ---------------------------------------------------------------------------1-LOCATION_KEY----2- API KEY ---------------------------
DAY1_DAILY_FORCAST_URL = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{}?apikey={}&language=EN-IN&details=true&metric=true'
# -------------------------------------------------------------------------1 - location key ---2 - api key ----------------------------------- 
NEXT_5DAY_FORECAST_URL = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{}?apikey={}&language=en-in&details=true&metric=true'
# -------------------------------------------------------placeholders : 1 = api key, 2 = Location Name--------------------------------------------- 
BASE_LOCATION_URL = 'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={}&q={}&language=en-in'
CITY_NEIGHBOUR_LOCATION_URL = 'http://dataservice.accuweather.com/locations/v1/cities/neighbors/{}?apikey={}&language=en-in'
# -------------------------------------------------------------------1- LOCATION_ KEY --------2 - API KEY ---------------------
PAST_6HR_W_URL = 'http://dataservice.accuweather.com/currentconditions/v1/{}/historical?apikey={}&language=en-in&details=true'
# -------------------------------------------------------------------1- LOCATION_ KEY --------2 - API KEY ---------------------
NEXT_12HR_F_URL = 'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{}?apikey={}&language=EN-IN&details=true&metric=true' 

# few_area_forcast
def get_neighbour_areas_weather(n_cities):
    n_area_weather = []
    for i in range(len(n_cities)):
        w_url = BASE_FORECAST_URL.format(n_cities[i]['location_key'], API_KEY)
        response = requests.get(w_url)        
        data = response.json()
        n_area_weather.append(
            {
                'city_name': n_cities[i]['city_name'],
                'state' : n_cities[i]['state'],
                'geo_location' : n_cities[i]['geo_location'],
                'temperature' : data[0]['Temperature']['Metric']['Value'],
                'real_feel': data[0]['RealFeelTemperature']['Metric']['Value'],
                'real_feel_phrase' : data[0]['RealFeelTemperature']['Metric']['Phrase'],
                'humidity' : data[0]['RelativeHumidity'],
                'wind_direction' : f"{data[0]['Wind']['Direction']['Degrees']}° {data[0]['Wind']['Direction']['Localized']}",
                'wind_speed' : f"{data[0]['Wind']['Speed']['Metric']['Value']} {data[0]['Wind']['Speed']['Metric']['Unit']}",
                'precipitation' : f"{data[0]['PrecipitationSummary']['Precipitation']['Metric']['Value']} {data[0]['PrecipitationSummary']['Precipitation']['Metric']['Unit']}"
            }
        )
    return n_area_weather    

def get_neighbour_to_city_keys():
    location_key = '2898823'
    n_url = CITY_NEIGHBOUR_LOCATION_URL.format(location_key, API_KEY)
    response = requests.get(n_url)
    data = response.json()   
    location_keys = []
    if data:
        for i in range(len(data)):
            location_keys.append({'location_key':data[i]['Key'], 'city_name': data[i]['LocalizedName'], 'state':data[i]['AdministrativeArea']['LocalizedName'], 'geo_location':f"{data[i]['GeoPosition']['Latitude']}, {data[i]['GeoPosition']['Longitude']}"})
        if location_keys:
            local_weather_forcast_list = get_neighbour_areas_weather(location_keys)
            if local_weather_forcast_list:
                return local_weather_forcast_list
            else:
                return location_keys
        else:
            return location_keys
    else:
        return location_keys

@app.route('/')
def home():
    session.clear()    
    n_city_info = get_neighbour_to_city_keys()
    if n_city_info:
        random_city_info = random.sample(n_city_info, 4)
    return render_template('index.html', random_city_info = random_city_info)

def get_city_details(city):
    session.clear()
    session['city'] = city
    #-------------------------------- 1 - API_key, 2 - City Name
    try:
        location_url = BASE_LOCATION_URL.format(API_KEY, city)
        geo_data_response = requests.get(location_url)
        geo_data = geo_data_response.json()
        session['city_info'] = geo_data
        return geo_data[0]['Key']
    except:
        return redirect(url_for('home'))
        
def get_1day_daily_forecast(l_key):
    url = DAY1_DAILY_FORCAST_URL.format(l_key, API_KEY)
    ddf_response = requests.get(url)
    ddf_data = ddf_response.json()
    session['day1_daily_forecast'] = ddf_data    
    return   

def get_weather_details_of_city(l_key):
    #-------------------------------- 1 - location_key, 2 - API_key
    weather_url = BASE_FORECAST_URL.format(l_key, API_KEY)
    w_data_response = requests.get(weather_url)
    w_data = w_data_response.json()
    session['weather_info'] = w_data
    return

def get_neighbour_cities(l_key):
    n_city_url = CITY_NEIGHBOUR_LOCATION_URL.format(l_key, API_KEY)
    n_city_data_response = requests.get(n_city_url)
    n_city_data = n_city_data_response.json()
    n_city_list = []
    for i in range(len(n_city_data)):
        n_city_list.append({
            'location_key':n_city_data[i]['Key'], 
            'city_name': n_city_data[i]['LocalizedName'], 
            'state': n_city_data[i]['AdministrativeArea']['LocalizedName'], 
            })
    session['neighbour_cities'] = n_city_list    
    return 

def get_next12hr_forecast(l_key):
    next12hr_url = NEXT_12HR_F_URL.format(l_key, API_KEY)
    next_12hr_response = requests.get(next12hr_url)
    next12hr_data = next_12hr_response.json()
    next_12hr_f_list = []
    for i in next12hr_data:
        next_12hr_f_list.append(i)
    session['next_12hr_forecast'] = next_12hr_f_list
    return

@app.route('/show_weather')
def show_weather():
    current_date = dt.datetime.now().strftime("%d-%b-%Y,%I:%M:%S %p").split(',')
    return render_template('weather_forecast.html', c_date = current_date)

@app.route('/get_weather', methods = ['POST'])
def get_weather():
    city = request.form.get('city').strip().lower()
    try:
        l_key = get_city_details(city)
        get_weather_details_of_city(l_key)
        get_neighbour_cities(l_key)
        get_1day_daily_forecast(l_key)
        get_next12hr_forecast(l_key)
        return redirect(url_for('show_weather'))
    except:
        return redirect(url_for('home'))
    
@app.route('/get_weather_n_city/<city>')
def get_weather_n_city(city):
    l_key = get_city_details(city)
    get_weather_details_of_city(l_key)
    get_neighbour_cities(l_key)
    get_1day_daily_forecast(l_key)    
    return redirect(url_for('show_weather'))

@app.route('/past_6hr_condtion')
def past_6hr_condtion():
    l_key = session['city_info'][0]['Key']
    past_6hr_weather_url = PAST_6HR_W_URL.format(l_key ,API_KEY)
    p_6hr_weather_response = requests.get(past_6hr_weather_url)
    p_6hr_weather_data = p_6hr_weather_response.json()
    current_date = dt.datetime.now().strftime("%d-%b-%Y,%I:%M:%S %p").split(',')
    return render_template('past_6hr_weather.html', p_data = p_6hr_weather_data, c_date = current_date)

@app.route('/next_5day_forecast')
def next_5day_forecast():
    l_key = session['city_info'][0]['Key']
    n5_weather_url = NEXT_5DAY_FORECAST_URL.format(l_key, API_KEY)
    n5_weather_response = requests.get(n5_weather_url)
    n5_weather_data = n5_weather_response.json()
    current_date = dt.datetime.now().strftime("%d-%b-%Y,%I:%M:%S %p").split(',')
    return render_template('next_5day_forecast.html', n5_data = n5_weather_data, c_date = current_date)

@app.route('/important_info')
def important_info():    
    current_date = dt.datetime.now().strftime("%d-%b-%Y,%I:%M:%S %p").split(',')
    return render_template('important_info.html', c_date = current_date)

# ========================================================================================
if __name__ == '__main__':
    app.run(debug=True)
  