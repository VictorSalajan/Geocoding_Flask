from flask import Flask, render_template, request, redirect, url_for
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from folium.plugins import MarkerCluster
from urllib.request import urlopen
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/display_euro_capitals/')
def display_euro_capitals():
    try:
        return render_template('european_capitals.html')
    except:
        url = 'https://en.wikipedia.org/wiki/Template:Capital_cities_of_European_Union_member_states'
        page = urlopen(url)
        html = page.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        tbodies = soup.find_all('tbody')

        countries_and_capitals = []
        for i, tbody in enumerate(tbodies):
            if i == 0:
                pass
            else:
                tds = tbody.find('td')
                ahrefs = tds.find_all('a')
                country = ahrefs[0]['title']
                capital = ahrefs[1]['title']
                countries_and_capitals.append((country, capital))

        geolocator = Nominatim(user_agent='map_scraped_capitals')

        m = folium.Map()
        for loc_tuple in countries_and_capitals:
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
            country, capital = loc_tuple[0], loc_tuple[1]
            location = {'country': country, 'city': capital}
            coordinates = geocode(location)
            lat, lon = coordinates.point.latitude, coordinates.point.longitude
            tooltip = f'{country}: {capital}'
            folium.Marker([lat, lon], tooltip=tooltip).add_to(m)
        m.save('templates/european_capitals.html')
        return render_template('european_capitals.html')

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
