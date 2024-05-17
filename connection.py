import requests
import json
import os
from rich import print
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("SCRAPPEY_KEY")

headers = {'Content-Type': 'application/json'}
scrappey = f"https://publisher.scrappey.com/api/v1?key={key}"

#TODO add banned validation

#----- Main ----
""" ---INFO---
    "data" parameter must like this:
    data = {
        "cmd" : "request.get",
        "url" : f"{url}",
        "requestType" : "request",
        "proxyCountry" : "UnitedStates" (optional)
        "proxy" : proxy (optional)
    }

    if you use a "proxy" parameter, remove "proxyCountry"
"""
async def get_data(data):
    options = data
    try:
        response = requests.post(scrappey, headers=headers, json=options)
        return response.json()
    except(ValueError, json.decoder.JSONDecodeError):
        print("Error")
        print(response)
        return None
#----- Main ----

#----- Alternatives -----
#----- Alternatives -----