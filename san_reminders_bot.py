# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 18:15:38 2020
@author: this_
"""
#---------------------------------------------------------------------------------------------------------------
#One user to one common file token for now

#TODO:

#To implement:
#1. Multiple user and token storage
#2. Periodic notifications
#3. Reading event details
#4. make your bot reply to message keywords

#----------------------------------------------------------------------------------------------------------------

#import all the libs

from __future__ import print_function
import os
import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

#----------------------------------------------------------------------------------------------------------------

#initialise google calendar api nonsense
import datetime

client_secrets='' #rmb to hide this
SCOPES='https://www.googleapis.com/auth/calendar.readonly' #read only

#---------------------------------------------------------------------------------------------------------------

#initialising telegram bot nonsense
token1="" #hide this too
import telegram
bot = telegram.Bot(token=token1)
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters #to process received messages, not just commands
from telegram.ext import InlineQueryHandler #to process inline queries
from telegram import InlineQueryResultArticle, InputTextMessageContent

updater = Updater(token=token1, use_context=True)
dispatcher = updater.dispatcher

#----------------------------------------------------------------------------------------------------------------

#start handler everytime you start the bot /start
def start(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your Google Calendar linked Gmail account (example123@gmail.com)")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Authenticating you to Google Calendar...")
    launch_browser = True
    
    client_secrets='client_secret_434636886184-9dgh3kd20f3k51uduor3eg6s79i1dse8.apps.googleusercontent.com.json' #rmb to hide this
    SCOPES='https://www.googleapis.com/auth/calendar.readonly'
    
    appflow = InstalledAppFlow.from_client_secrets_file(client_secrets,scopes=[SCOPES])
    
    if launch_browser:
        appflow.run_local_server()
        creds=appflow.credentials
        with open('token.pickle', 'wb') as token_cal:
            pickle.dump(creds, token_cal)
    else: #in case of errors
        appflow.run_console()

    context.bot.send_message(chat_id=update.effective_chat.id, text="Authenticated to Google Calendar. What can I remind you of today?")

start_handler=CommandHandler('start',start)
dispatcher.add_handler(start_handler)

#----------------------------------------------------------------------------------------------------------------

#test handler to make sure bot is working /now
def now(update,context):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    context.bot.send_message(chat_id=update.effective_chat.id, text=now)

now_handler=CommandHandler('now',now)
dispatcher.add_handler(now_handler)

#----------------------------------------------------------------------------------------------------------------

#fetch next 10 events (make sure google api is working)
def fetch10(update,context):
#everytime you call the service you need to call the token - when you have multiple users, need to rename tokens
   with open('token.pickle', 'rb') as token_cal:
        creds = pickle.load(token_cal)
   service = build('calendar', 'v3',credentials=creds, cache_discovery=False)
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

#sync new account
def addnew(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Sync to new calendar?')
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Previous account removed! Please run /start again to authenticate your new account.')

addnew_handler=CommandHandler('addnew',addnew)
dispatcher.add_handler(addnew_handler)

#--------------------------------------------------------------------------------------------------------------

#readtext and respond
def createnew(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Name of new event?')
createnew_handler=CommandHandler('createnew',createnew)
dispatcher.add_handler(createnew_handler)

#respond - template; change this to whatever you want it to respond

def respond(update, context):
    name=update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text=(name+'123'))
response_handler = MessageHandler(Filters.text & (~Filters.command), respond)
dispatcher.add_handler(response_handler)

#---------------------------------------------------------------------------------------------------------------

#command exception handler
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

#----------------------------------------------------------------------------------------------------------------
#try inline queries

def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)
    
inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

#----------------------------------------------------------------------------------------------------------------
#guess i'll just deploy it on the PI instead of the webhook method

#start bot
updater.start_polling()
