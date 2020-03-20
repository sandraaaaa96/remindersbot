# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 18:15:38 2020

@author: this_
"""

from __future__ import print_function
from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

#----------------------------------------------------------------------------------------------------------------

#initialise google calendar api nonsense
import datetime
import pickle
import os.path

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token_cal:
        creds = pickle.load(token_cal)

#creates the calendar instance to tap into
service = build('calendar', 'v3', credentials=creds, cache_discovery=False) 

#---------------------------------------------------------------------------------------------------------------

#initialising telegram bot nonsense
token1="1121399263:AAEeEzDX8Q0B-JmO04XM7ztU_8o0ffxAL38"
import telegram
import logging
bot = telegram.Bot(token=token1)
from telegram.ext import Updater
from telegram.ext import CommandHandler
updater = Updater(token=token1, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#----------------------------------------------------------------------------------------------------------------

#start handler everytime you start the bot /start
def start(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello Sandra. What can I remind you of today?")

start_handler=CommandHandler('start',start)
dispatcher.add_handler(start_handler)

#----------------------------------------------------------------------------------------------------------------

#test handler to call google calendar api /now
def now(update,context):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    context.bot.send_message(chat_id=update.effective_chat.id, text=now)

now_handler=CommandHandler('now',now)
dispatcher.add_handler(now_handler)

#----------------------------------------------------------------------------------------------------------------

#fetch next 10 events (google calendar example)
def fetch10(update,context):
   context.bot.send_message(chat_id=update.effective_chat.id, text='Getting the upcoming 10 events')
   # 'Z' indicates UTC time, google cal seems to only read this in 
   now = datetime.datetime.utcnow().isoformat() + 'Z' 
   events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
   events = events_result.get('items', [])
   if not events:
       context.bot.send_message(chat_id=update.effective_chat.id, text='No upcoming events found.')
       
       #TODO: edit this text field to print all in one message
   for event in events:
       start_date = event['start'].get('date')
       print_events = "%s, %s" %(start_date,event['summary'])
       context.bot.send_message(chat_id=update.effective_chat.id, text=print_events)

fetch10_handler=CommandHandler('fetch10',fetch10)
dispatcher.add_handler(fetch10_handler)

#--------------------------------------------------------------------------------------------------------------

#create new event in calendar
#def new_event(update,context):
        

#start bot
updater.start_polling()


