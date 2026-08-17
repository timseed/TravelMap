# TavelMap

I wanted a simple way to keep track of where myself and friends have visited. So we can plan fresh trips.

I did not want to use on-line services, instead the data is self hosted.

# Python

I am running 3.10, the dependancies are listed in *requirements.txt*

## Data

I downloaded the following files

    - ne_110m_admin_0_countries.zip 
    - cities500.zip 

I forget from where - but they are easy to find.

### Convert admin into Db

I ran the python script **admin_countries_ti_db.py**

This creates a database called **cities.db** which is sqlite3.

### Add the Cities500 data

I now run via python **add_cities.py**, this creates a new table in the existing database (note: It does not create the Db so this part needs to be done when the Db exists).

# Build the Map

Just run **map.py**

Pay attention for the screen output as this will indicate Cities that can not be matched.

Cities that can not be geolocated will appear as  lines such as  

```txt
UNK: Malaga ES 
```

# Add new places you have visited

 Just edit the XML. Data is grouped by *user*, with a child node of *visited* followed by a list of place. Each place Has to be a country, and then optionally a country can have a sub list of city.

Example:

Bob has visited 2 countries. France, and Korea.

In France he lists 2 cities having been visited, one with a date. Korea only the Country is noted as having been visited.

```XML
<?xml version="1.0" encoding="UTF-8"?>
<users>
  <user name="Bob">
    <visited>
      <place country="FR">
        <city name="Paris"/>
        <city name="Lyon">
           <date>2012-02</date>
        </city>
      </place>
      <place country="KR"/>
    </visited>
  </user>
</users>
```

The Country will be marked in blue on the output, the cities as Red Dots.

## City Names are not unique

*New York* has 3 entries in the cities.Db so I always pick the place with the biggest population.
