import os.path
import requests
import gspread
import pandas as pd
import numpy as np
import datetime as datetime
import functions as mf

gc = gspread.service_account(filename='service_account.json')

worksheet2020 = gc.open('2020 Sneeze Survey')
# test= pd.DataFrame(worksheet2020.sheet1.get_all_values())
# test.to_json("data/test.json", orient='records', lines =True)
array2020 = np.array(worksheet2020.sheet1.get_all_values())


worksheet2021 = gc.open('2021 Sneeze Survey')
array2021 = np.array(worksheet2021.sheet1.get_all_values())

np.savetxt("data/2020Sneezes.csv",array2020,delimiter=";",fmt='%s')	
np.savetxt("data/2021Sneezes.csv",array2021,delimiter=";",fmt='%s')
