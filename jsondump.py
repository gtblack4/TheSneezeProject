import json
from urllib.request import urlopen

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
with open('data/counties-fips.json',"w") as outfile:
    json.dump(counties,outfile)