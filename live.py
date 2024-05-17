from db import db
from rich import print
from tabulate import tabulate

async def get_live_events():
    res = db.table("matches").select("*").eq("status", "Live").execute()
    if len(res.data) > 0:
        formatted = await live_matches_formatter(data=res.data)
        return formatted
    return None

#Format events to send a correct live table
async def live_matches_formatter(data):
    #This merge option groups the events by tournaments, so that formatted message can look better and uses less characters
    group = await live_merger(data=data)
    print(group)


async def live_merger(data):
    print(f"Merging events from: {data[0]['tournament']}")
    merged_list = []

    for entry in data:
        tournament_exists = False
        info = {
            "match_name" : entry['match_name'],
            "teamA" : entry['teamA'],
            "teamB" : entry['teamB'],
            "scoreboard" : {}
        }
        
        for item in merged_list:
            if item['tournament'] == entry['tournament']:
                tournament_exists = True
                item['events'].append(info)
                break
        
        if not tournament_exists:
            print(f"{entry['tournament']} not in list, adding...")
            merged_list.append({'tournament' : entry['tournament'], 'events' : [info]})
        else:
            print(f"{entry['tournament']} already in list, adding event...")

    return merged_list

async def scores(match_id, match_name):
    print(f"Getting scores for match: {match_name}")
    