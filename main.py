from flask import Flask, render_template, request, redirect, url_for
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from folium.plugins import MarkerCluster

app = Flask(__name__)

global_nr_of_points = []
points = {}
@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        nr_of_points = request.form['nr_of_points']
        global_nr_of_points.append(nr_of_points)

        return redirect(url_for('pick_locations'))
    return render_template('home.html')

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
    geolocator = Nominatim(user_agent='flask_geo_app')
    m = folium.Map()

    for loc_name, address in points.items():
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        loc = geocode(address)
        lat, lon = loc.point.latitude, loc.point.longitude
        tooltip = f'Location: {loc_name}'
        folium.Marker([lat, lon], tooltip=tooltip).add_to(m)

    m.save('templates/geomapping.html')
    return render_template('geomapping.html')

if __name__ == "__main__":
    app.run(debug=True)
