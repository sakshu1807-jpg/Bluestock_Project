import os
import pandas as pd
import requests

def fetch_live_and_save(scheme_name: str, scheme_code: int) -> pd.DataFrame | str:
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"fetching the data from the scheme name as {scheme_name} with code {scheme_code}")

    try:
        response = requests.get(url, timeout= 20)

        if response.status_code == 200:
            json_data = response.json()
            
            df = pd.DataFrame(json_data['data'])
            filepath = f'C:/Users/DELL/VS CODE/project/data/raw/{scheme_name.lower().replace(' ','_')}.csv'

            df.to_csv(filepath, index=False)
            print("File saved successfully !!")

    except Exception as error:
        return f"Failed to fetch data from {url}. Error :- {str(error)}"

scheme_to_fetch = {
        125497: "HDFC Top 100 Direct",
        119551: "SBI Bluechip",
        120503: "ICICI Bluechip",
        118632: "Nippon Large Cap",
        119092: "Axis Bluechip",
        120841: "Kotak Bluechip"
}

for code, name in scheme_to_fetch.items():
    try:
        fetch_live_and_save(name, code)
        print("All APIs are successfully extracted and saved !!!")
    except Exception as error:
        print(f"An error occurred as {str(error)}")