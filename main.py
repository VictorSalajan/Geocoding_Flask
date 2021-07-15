from flask import Flask, render_template, request, redirect, url_for
from os import path
from scrape_and_map import *
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


app = Flask(__name__)

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
        return 'No map exists. Go to "Generate & Display a map of countries, capitals & GDP per capital" link'
    return render_template('country_cap_gdp_per_capita.html')

@app.route('/display_generate_countries_capitals_gdp_per_capita/')
def display_generate_country_cap_gdp_per_capita():
    """ Creates country DataFrame, Rescrapes & matches data, generates coordinates & maps them """
    create_country_df()
    scrape_country_gdp()
    match_country_capital()     # calls scrape_capitals()
    geocode_coordinates()
    geomap_country_gdp()
    return render_template('country_cap_gdp_per_capita.html')


@app.route('/visualize_latitude_gdp_relationship/')
def visualize_latitude_gdp():
    df = pd.read_csv('country_db.csv')
    df.dropna(inplace=True)
    df['gdp_per_capita'] = df['gdp_per_capita'].apply(lambda x: int(x.replace(',', '')))
    x, y = df['latitude'], df['gdp_per_capita']
    correlation, p_value = stats.pearsonr(x, y)

    sns.scatterplot(x='latitude', y='gdp_per_capita', size="gdp_per_capita", sizes=(30, 800), data=df, legend=None)
    plt.savefig('static/latitude_gdp_relationship.jpg')

    d = {0.001: '< .001', 0.01: '< .01', 0.05: '< .05'}
    for k, v in d.items():
        if p_value < k:
            p_value = v
            break
        else:
            p_value = round(p_value, 2)

    context = {'correlation': format(correlation, '.2f'), 'p_value': p_value}
    return render_template('latitude_gdp_relationship.html', **context)


if __name__ == "__main__":
    app.run(debug=True)
