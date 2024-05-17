from db import db
from rich import print
from tabulate import tabulate
import json

async def get_live_events():
    res = db.table("matches").select("*").eq("status", "Live").execute()
    if len(res.data) > 0:
        formatted = await live_matches_formatter(data=res.data)
        return formatted
    else:
        return None

#Format events to send a correct live table
async def live_matches_formatter(data):
    #This merge option groups the events by tournaments, so that formatted message can look better and use less characters
    group = await live_merger(data=data)
    if len(group) > 0:
        for tournament in group:
            formatted = format_tournament(tournament=tournament)
            table_output = "\n".join(formatted)
            code_block = f"""```
            {table_output}
            ```"""
            return code_block


async def live_merger(data):
    print(f"Merging events from: {data[0]['tournament']}")
    merged_list = []

    for entry in data:
        tournament_exists = False
        info = {
            "match_name" : entry['match_name'],
            "teamA" : entry['teamA'],
            "teamB" : entry['teamB'],
            "scoreboard" : scores(entry['match_id'], entry['match_name']) 
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

def scores(match_id, match_name):
    print(f"Getting scores for match: {match_name}")
    res = db.table("scoreboard").select("*").match({'match_id': match_id, 'match_name': match_name}).execute()
    if len(res.data) > 0:
        event = res.data[0]
        scores = {
            'period' : event['current_period'],
            'set_one_teamA_score': event['set_one_teamA_score'],
            'set_one_teamB_score': event['set_one_teamB_score'],
            'set_two_teamA_score': event['set_two_teamA_score'],
            'set_two_teamB_score': event['set_two_teamB_score'],
            'set_three_teamA_score': event['set_three_teamA_score'],
            'set_three_teamB_score': event['set_three_teamB_score'],
        }
    return scores

def format_tournament(tournament):
    print(f"Formatting live tournament: {tournament['tournament']}")
    formatted_event = []
    #This will be the title
    formatted_event.append(f"{tournament['tournament'].upper()}\n")
   #And this is the list of events
    for match in tournament['events']:
        header = [
                f"{match['scoreboard']['period']}",
                "*",
                "1st",
                "2nd",
                "3rd"
                #TODO add optional 4th and 5th set
            ]

        first_row = [
                f"{match['teamA']}",
                "*",
                f"{match['scoreboard']['set_one_teamA_score']}",
                f"{match['scoreboard']['set_two_teamA_score']}",
                f"{match['scoreboard']['set_three_teamA_score']}"
            ]

        second_row = [
                f"{match['teamB']}",
                "*",
                f"{match['scoreboard']['set_one_teamB_score']}",
                f"{match['scoreboard']['set_two_teamB_score']}",
                f"{match['scoreboard']['set_three_teamB_score']}"           
            ]

            #unify the table
        body = [header, first_row, second_row]
        score_table = tabulate(body, tablefmt="simple")
        formatted_event.append(f"{match['match_name']}\n{score_table}\n")

    return formatted_event

