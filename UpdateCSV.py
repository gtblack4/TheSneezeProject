import os.path
import json
import gspread
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials



def updateSpeadsheet():
	if os.getenv('ENVIRON') == "PROD":
		json_creds = os.getenv("CREDS")
		creds_dict = json.loads(json_creds)
		creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
		creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
		gc = gspread.authorize(creds)

	else:
		#gc = gspread.service_account_from_dict(os.getenv('ENVIRON'))
		gc = gspread.service_account(filename='service_account.json')
		

	worksheet2020 = gc.open('2020 Sneeze Survey')
	# test= pd.DataFrame(worksheet2020.sheet1.get_all_values())
	# test.to_json("data/test.json", orient='records', lines =True)
	array2020 = np.array(worksheet2020.sheet1.get_all_values())


	worksheet2021 = gc.open('2021 Sneeze Survey')
	array2021 = np.array(worksheet2021.sheet1.get_all_values())

	worksheet2022 = gc.open('2022 Sneeze Survey')
	array2022 = np.array(worksheet2022.sheet1.get_all_values())



	np.savetxt("data/2020Sneezes.csv",array2020,delimiter=";",fmt='%s')	
	np.savetxt("data/2021Sneezes.csv",array2021,delimiter=";",fmt='%s')
	np.savetxt("data/2022Sneezes.csv", array2022, delimiter=";", fmt='%s')
	sneezeData2020 =pd.read_csv('data/2020Sneezes.csv',sep=";")
	sneezeData2021 =pd.read_csv('data/2021Sneezes.csv',sep=";")
	sneezeData2022 =pd.read_csv('data/2022Sneezes.csv',sep=";")

updateSpeadsheet()