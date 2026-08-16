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
    print(f"Filtering for {username}")
    for user in root.findall("user"):
        if user.get("username") != username:
            continue
        print(f"Places visited by {username}:")

        places = user.find("visited")
        for place in places.findall("place"):
            country = place.get("country")
            for city in place.findall("city"):
                name = city.get("name")
                date_element = city.find("date")
                date = date_element.text if date_element is not None else None

                cities.append({
                    "city": name,
                    "country": country,
                    "date": date
                })
            date_element = place.find("date")
            if date_element is not None:
                date = date_element.text
            else:
                date = None

            print(country, date)
            rv.append(country)
    return rv,cities



# Load world boundaries
world = gpd.read_file("ne_110m_admin_0_countries.zip")
for p in ["juliet","tim"]:
    # Countries you have visited
    visited,cities = read_places(who=p)

    # Separate visited countries
    visited_gdf = world[world["NAME"].isin(visited)]


    
    # --------------------------------------------------
    # Geocode cities
    # --------------------------------------------------
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor() 
    for city in cities:
        query = "SELECT * FROM cities where name=? and county_code=?"
        cursor.execute(query, city['city'], city['country'])
    
        # Fetch all matching rows
        results = cursor.fetchall()
        if len(results)==0:
            print(f"error nothing found for {city['city']} in {city['country']}")
        elif len(results)>1:
            print(f"Multiple records found for {city['city']} in {city['country']}")
        else:
            if location:
                city["lat"] = results[0].latitude
                city["lon"] = results[0].longitude


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

    for city in cities:

        if "lat" not in city:
            continue

        popup = f"<b>{city['city']}</b><br>"
        popup += f"{city['country']}"

        if city["date"]:
            popup += f"<br>Visited: {city['date']}"

        folium.CircleMarker(
            location=[
                city["lat"],
                city["lon"]
            ],
            radius=5,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.9,
            popup=popup
        ).add_to(m)


    # Save web page
    m.save(f"{p}_visited_places.html")
