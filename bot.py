from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
import requests
import discord
import logging
import os

def TomorrowDateString() -> str:
    return (datetime.now() + timedelta(days=1)).strftime('%m-%d-%Y')

def getLectionaryData() -> dict:
    entries = {}
    resp = requests.get("https://www.stmarysnova.org/indian-orthodox-lectionary", headers={'User-Agent': 'Chrome'})

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, features='html.parser')
        day_boxes = soup.find_all('div', class_='DayBox')

        for day_box in day_boxes:
            raw_date = day_box.select('h3')[0].text.split(':')[0]
            entry_date_month_day = datetime.strptime(raw_date, '%B-%d')
            entry_date = entry_date_month_day.replace(year=datetime.now().year)
            entries[entry_date.strftime('%m-%d-%Y')] = day_box.text.strip()
    else:
        logging.warning(r'Unknown status code received when fetching lectionary data: {resp.status_code}')

    return entries

def getTomorrowsReading(lectionaryData: dict):
    tomorrow = TomorrowDateString()
    if tomorrow in lectionaryData.keys():
        return lectionaryData[tomorrow]
    else:
        return None

TOKEN = os.environ.get('DISCORD_TOKEN')
LECTIONARY_CHANNEL = 1117619969560162354

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', intents=intents)

client = commands.Bot(("prefix"), intents=discord.Intents.all())

@tasks.loop(hours=24)
async def tomorrows_reading():
    lectionary_channel = client.get_channel(LECTIONARY_CHANNEL)

    lectionaryData = getLectionaryData()
    tomorrowsReading = getTomorrowsReading(lectionaryData)
    if tomorrowsReading != None:
        logging.info('Sending tomorrow\'s reading')
        await lectionary_channel.send(tomorrowsReading)
    else:
        logging.info('No reading for tomorrow')


@tomorrows_reading.before_loop
async def before_tomorrows_reading():
    await client.wait_until_ready()  # Wait until bot is ready.

@client.event
async def on_ready():
    print(f'Bot is ready. Client: {client.user}')
    tomorrows_reading.start()

client.run(TOKEN)

