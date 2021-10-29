import requests
import urllib
import numpy as np
import pandas as pd
#Sample latitude and longitudes

lat = 40
lon = -75

#Encode parameters
sneezeData2020 =pd.read_csv('data/2020Sneezes.csv',sep=";")

sneezeData2021 =pd.read_csv('data/2021Sneezes.csv',sep=";")
if ('GeoCode' in sneezeData2021.columns):
    sneezeData2021[['latitude', 'longitude']] = sneezeData2021['GeoCode'].str.split(",", expand=True)
    sneezeData2021['latitude'].apply(lambda x: float(x))
    sneezeData2021['longitude'].apply(lambda x: float(x))


sneezeData2020 = sneezeData2021
#sneezeData2020 = sneezeData2020.append(sneezeData2021)

fipsData2020 = []
finalfips = []
for x in range(0, len(sneezeData2020)):
    if (str(sneezeData2020['latitude'][x])) != 'nan':
        print(sneezeData2020['latitude'][x])
        params = urllib.parse.urlencode({'latitude': sneezeData2020['latitude'][x], 'longitude':sneezeData2020['longitude'][x], 'format':'json'})
        print("--------------------------------------")
#Contruct request URL
        url = 'https://geo.fcc.gov/api/census/block/find?' + params
        print(url)
#Get response from API
        response = requests.get(url)

#Parse json in response
        data = response.json()

        fip = data['County']['FIPS']
#Print FIPS code
    else:
        fip = 0
    fipsData2020.append([sneezeData2020['Number of Sneezes'][x], fip])

finalfips = pd.DataFrame(fipsData2020)
finalfips.columns=['sneezes','fips']
finalfips = finalfips.groupby(['fips']).sum()
finalfips.to_csv('data/allFips.csv')
# with open("2020FipsFile.txt", "w") as output:
#     output.write(str(finalfips))


