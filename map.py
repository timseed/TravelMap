import geopandas as gpd
import folium
from geopy.geocoders import Nominatim
import xml.etree.ElementTree as ET
import sqlite3


def read_places(who="tim"):
    """
    return two lists. First is countries, the 2nd is cities.
    """
    tree = ET.parse("visited.xml")
    root = tree.getroot()
    rv = []
    cities = []
    username = who
#    print(f"Filtering for {username}")
    for user in root.findall("user"):
        if user.get("username") != username:
            continue
        print(f"Places visited by {username}:")

        places = user.find("visited")
        for place in places.findall("place"):
            country = place.get("country")
            rv.append(country)
            for city in place.findall("city"):
                name = city.get("name")
                date_element = city.find("date")
                date = date_element.text if date_element is not None else None

                cities.append({"city": name, "country": country, "date": date})
            date_element = place.find("date")
            if date_element is not None:
                date = date_element.text
            else:
                date = None

#            print(country, date)
            rv.append(country)

    return list(set(rv)), cities


def city_position(cities) -> list:
    """
    read_places returns a cities value (2nd value)
    Using this, we connect to a local SQLITE Db, and look up the city name.
    If it is in the local db, we add the city along with the lat and the long
    to an output list of dictionary objects.

    Output will look something like this
    [{'city': 'Bilbao', 'lat': 43.26271, 'lon': -2.92528},
     {'city': 'London', 'lat': 51.50853, 'lon': -0.12574}]

    """
    conn = sqlite3.connect("cities.db")
    cursor = conn.cursor()
    # Order by Population Desc
    query = "SELECT * FROM cities where name=? and country_code=? order by population desc "
    city_plot = []
    for c in cities:
        cursor.execute(query, (c["city"], c["country"]))
        results = cursor.fetchall()
        if len(results) !=0:
            #print(f"{results}")
            if len(results)>1:
                print(f"Multi city {c['city']} picking biggest")
            city_plot.append(
                {"city": c["city"], "lat": results[0][6], "lon": results[0][7]}
            )
        else:
            print(f"Unk: {c['city']} {c['country']}")
    return city_plot


# Load world boundaries
world = gpd.read_file("ne_110m_admin_0_countries.zip")
for p in ["juliet", "tim"]:
    # Countries you have visited
    visited, cities = read_places(who=p)
    # Now convert the Cities in the XML to cities with Lat and Long
    city_plot = city_position(cities)

    # Separate visited countries using the A2 code i.e. FR, DE or NL
    visited_gdf = world[world["ISO_A2"].isin(visited)]

    # Create map
    m = folium.Map(location=[30, 0], zoom_start=2, tiles="CartoDB positron")

    # Add all countries in grey
    folium.GeoJson(
        world,
        style_function=lambda feature: {
            "fillColor": "#dddddd",
            "color": "#888888",
            "weight": 0.5,
            "fillOpacity": 0.5,
        },
    ).add_to(m)

    # Highlight visited countries
    folium.GeoJson(
        visited_gdf,
        style_function=lambda feature: {
            "fillColor": "#3388ff",
            "color": "#0055aa",
            "weight": 2,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["NAME"], aliases=["Visited:"]),
    ).add_to(m)
    ## --------------------------------------------------
    # Add city markers
    # --------------------------------------------------
    for city in city_plot:
        popup = f"<b>{city['city']}</b><br>"

        folium.CircleMarker(
            location=[city["lat"], city["lon"]],
            radius=5,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.9,
            popup=popup,
        ).add_to(m)

    # Save web page
    m.save(f"{p}_visited_places.html")
