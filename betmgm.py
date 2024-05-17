import asyncio
import json
from rich import print
from notifier import notification
from connection import get_data
from utils import verifier, remove_parentheses
from db import db

async def get_all_events():
    print("Getting BetMGM events...")
    #No need for proxy

    data = {
        'cmd' : 'request.get',
        'url' : f"https://sports.ny.betmgm.com/en/sports/api/widget/widgetdata?layoutSize=Large&page=SportLobby&sportId=5&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/sportgrid&shouldIncludePayload=true",
        'requestType' : 'request'
    }

    #Try at least five times
    attempt_count = 0
    while attempt_count < 5:
        try:
            response = await get_data(data=data)
            if response == None:
                print(f"Error getting BetMGM Data - Trying again")
                attempt_count += 1
            else:
                #use verifier function to check if the response is valid for parsing
                is_valid = verifier(value=response)
                if is_valid:
                    await main_parser(response=response)
                    break
                else:
                    attempt_count += 1
                    print("Error in BetMGM - Response is not valid for parsing")
                    raise RuntimeError("Response is not valid for parsing")
        except Exception as e:
            if attempt_count == 4:
                notification(f"Error on BetMGM - {e}")
            attempt_count += 1

        
#---- Parsers ----
async def main_parser(response):
    #We get all matches on the matches table and divide them by their status: Live or Prematch
    matches_table = db.table("matches").select("match_name").execute()
    #Create a list with only the matches names, this field is unique, and needs to be retrieved to avoid duplicate matches
    matches_names = [item['match_name'] for item in matches_table.data]
    if 'response' in response['solution']:
        load = json.loads(response['solution']['response'])
        
        #make sure everything exists before parsing
        try:
            if 'widgets' in load and 'payload' in load['widgets'][0] and 'fixtures' in load['widgets'][0]['payload']:
                fixtures = load['widgets'][0]['payload']['fixtures']
                
                #Check if match exists in table before posting or updating
                for match in fixtures:
                    #Use the remove parenthesis function since matches names tend to look like this: Nicolas Jarry (CHI) - Tommy Paul (USA)
                    match_name = remove_parentheses(match['name']['value'])
                    if match_name not in matches_names:
                        await post_match(match=match)
                    else:
                        await update_match(match=match)
            
        except Exception as e:
            print("Error in BetMGM parser", e)
            raise RuntimeError("error parsing BetMGM events")
    else:
        raise RuntimeError("there's not response in solution")
    
#----- Matches - live and schedule ------
async def post_match(match):
    print(f"Posting match: {match['name']['value']}")

    #create match format
    match_info = {
        "match_id" : match['id'],
        "match_name" : match['name']['value'],
        "tournament" : match['tournament']['name']['value'],
        "tournament_display_name": match['competition']['name']['value'],
        "status" : "Live" if match['stage'] == "Live" else "Not Started",
        "date" : match['startDate'],
        #sometimes the matches don't show the players at first, in that case we'll use "Unknown" to avoid errors and crashes
        "teamA" : remove_parentheses(match['participants'][0]['name']['value']) if len(match['participants']) > 0 else "Unknown",
        "teamB" : remove_parentheses(match['participants'][1]['name']['value']) if len(match['participants']) > 1 else "Unknown"
    }
    
    #Post it to the database
    db.table("matches").insert(match_info).execute()

    #We get the scores into a different table, just posting the ones with "Live" status
    scoreboard_info = {
        
    }


async def update_match(match):
    print(f"Updating match: {match['name']['value']}")

if __name__ == "__main__":
    try:
        asyncio.run(get_all_events())
    except RuntimeError as e:
        notification(f"Error on BetMGM - {e}")