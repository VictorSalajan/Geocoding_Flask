from urllib.request import urlopen
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from folium.plugins import MarkerCluster
from unidecode import unidecode
import pandas as pd
import numpy as np


geolocator = Nominatim(user_agent='flask_geo_app')
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def generate_euro_capitals():
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

    m = folium.Map()
    for loc_tuple in countries_and_capitals:
        country, capital = loc_tuple[0], loc_tuple[1]
        location = {'country': country, 'city': capital}
        coordinates = geocode(location)
        lat, lon = coordinates.point.latitude, coordinates.point.longitude
        tooltip = f'{country}: {capital}'
        folium.Marker([lat, lon], tooltip=tooltip).add_to(m)
    
    m.save('templates/european_capitals.html')

def generate_country_cap_gdp_per_capita():
    url = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)_per_capita'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    trs = soup.find_all('tr')
    countries = []
    gdp_per_capita = []
    for tr in trs:
        tds = tr.find_all('td')
        for j, td in enumerate(tds):
            # Scrape Countries
            if td.get('scope'):
                country = td.find('a')['title']
                countries.append(country)
            # Scrape GDP
            elif len(countries) > 0 and len(gdp_per_capita) < len(countries):
                if '2019' == td.contents[0]:
                    gdp = tds[j-1].contents[0]
                    gdp_per_capita.append(gdp)
                    break
                elif td == tds[-1]:
                    gdp_per_capita.append(np.nan)
                    break
    d = {'country': countries, 'gdp_per_capita': gdp_per_capita, 'capital': np.nan}
    df = pd.DataFrame(data=d)

    # Scrape capitals
    url = 'https://www.worlddata.info/capital-cities.php'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    rows = soup.find_all('tr')

    df['country'] = df['country'].apply(lambda x: unidecode(x))
    df.loc[df['country']=='Macau', ['country']] = 'Macao'
    df.loc[df['country']=='Czech Republic', ['country']] = 'Czechia'
    df.loc[df['country']=='Georgia (country)', ['country']] = 'Georgia'

    for row in rows:
        table_data = row.find_all('td')
        try:
            country = table_data[0].find('a').contents[0]
            capital = table_data[1].contents[0]
            if any(country in c for c in df.country.to_list()):
                index = df.index[df['country'].str.contains(country)]
                df.loc[index, 'capital'] = capital
        except:
            pass

    m = folium.Map()
    for country, capital, gdp in zip(df.country, df.capital, df.gdp_per_capita):
        location = {'country': country, 'city': capital}
        try:
            coordinates = geocode(location)
            lat, lon = coordinates.point.latitude, coordinates.point.longitude
        except:
            coordinates = geocode(country)
            lat, lon = coordinates.point.latitude, coordinates.point.longitude
        tooltip = f'{country}, {capital}: ${gdp}'
        folium.Marker([lat, lon], tooltip=tooltip).add_to(m)
    m.save('templates/country_cap_gdp_per_capita.html')
