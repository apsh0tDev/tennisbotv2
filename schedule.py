from db import db
from utils import format_datetime
import discord


async def get_schedule():
    res = db.table("matches").select("*").eq("status", "Not Started").execute()
    if len(res.data) > 0:
        formatted = await schedule_formatter(data=res.data)
        return formatted
    return None

#Format event to send a correct embed message
async def schedule_formatter(data):
        if len(data) > 0:
            fields_added = 0
            embeds = []
            current_embed = discord.Embed(title="Schedule 📅")
            for event in data:
                try:
                    event_name = event.get('match_name', '')
                    event_tournament = event.get('tournament', '')
                    event_date = format_datetime(event.get('date', ''))
                    if isinstance(event_name, str) and event_name.strip() != '' and isinstance(event_tournament, str) and event_tournament.strip() != '' and isinstance(event_date, str) and event_date.strip() != '':
                        field_value = f"{event_tournament} - {event_date}"
                        if len(current_embed) + len(event_name) + len(field_value) <= 6000 and fields_added < 25:
                            current_embed.add_field(name=event_name, value=field_value, inline=False)
                            fields_added += 1
                        else:
                            embeds.append(current_embed)
                            current_embed = discord.Embed(title="Schedule 📅")
                            fields_added = 0
                except Exception as e:
                    print("Error printing schedule: ", e)

            embeds.append(current_embed)  # Add the last embed if it's not empty
            for index, embed in enumerate(embeds):
                if index < 10:  # Limit to 10 embeds per message
                    return embed
                else:
                    print("Maximum number of embeds per message reached")
                    break
        else:
            return "No events scheduled."