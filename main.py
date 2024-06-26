import os

from flask import Flask, render_template, request, redirect, url_for
from os import path
from scrape_and_map import *
from stats_and_visuals import *
from linear_regression import *


crtDir = os.getcwd()
static_path = os.path.join('static')
app = Flask(__name__, static_folder=static_path)

@app.route('/')
def home():
    return render_template('home.html')

global_nr_of_points = []
points = {}
@app.route('/choose_points_nr/', methods=['POST', 'GET'])
def choose_points_nr():
    if request.method == "POST":
        nr_of_points = request.form['nr_of_points']
        global_nr_of_points.append(nr_of_points)
        return redirect(url_for('pick_locations'))
    return render_template('choose_points_nr.html')

@app.route('/pick_locations/', methods=['POST', 'GET'])
def pick_locations():
    nr_of_points = int(global_nr_of_points[0])
    if request.method == "POST":
        loc_name = request.form.getlist('loc_name')
        address = request.form.getlist('address')
        for x, y in zip(loc_name, address):
            points[x] = y
        return redirect(url_for('geocoding'))
    return render_template('pick_locations.html', nr_of_points=nr_of_points)

@app.route('/geo/')
def geocoding():
    m = folium.Map()
    for loc_name, address in points.items():
        loc = geocode(address)
        lat, lon = loc.point.latitude, loc.point.longitude
        tooltip = f'Location: {loc_name}'
        folium.Marker([lat, lon], tooltip=tooltip).add_to(m)
    m.save('templates/geomapping.html')
    return render_template('geomapping.html')

@app.route('/display_euro_capitals/')
def display_euro_capitals():
    if not(path.exists('templates/european_capitals.html')):
        return 'No map exists. Go to "Generate & Display a map of EU capitals" link'
    return render_template('european_capitals.html')

@app.route('/display_generate_euro_capitals/')
def display_generate_euro_capitals():
    generate_euro_capitals()
    return render_template('european_capitals.html')

@app.route('/countries_capitals_gdp_per_capita/')
def display_country_cap_gdp_per_capita():
    if not(path.exists('templates/country_cap_gdp_per_capita.html')):
        return 'No map exists. Go to "Generate & Display a map of countries, capitals & GDP per capita" link'
    return render_template('country_cap_gdp_per_capita.html')

@app.route('/display_generate_countries_capitals_gdp_per_capita/')
def display_generate_country_cap_gdp_per_capita():
    """ Creates country DataFrame, Rescrapes & matches data, generates coordinates & maps them """
    df = CountryData('country_db.csv')
    CountryData.gen_geomap_country_gdp(df)
    return render_template('country_cap_gdp_per_capita.html')

@app.route('/visualize_latitude_gdp_relationship/')
def visualize_latitude_gdp():
    gen_scatter_latitude_gdp()    # generate & save scatterplot image
    correlation, p_value = pearsonr_latitude_gdp()
    # linear regression metrics
    mae, rmse, coeff = metrics_pipeline()

    context = {'correlation': correlation, 'p_value': p_value, 'mae': mae, 'rmse': rmse, 'coeff': coeff}
    return render_template('latitude_gdp_relationship.html', **context)


if __name__ == "__main__":
    app.run(debug=True)
