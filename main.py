__author__ = "Maziyar Boustani"
__copyright__ = "Copyright 2023, The <company name>"
__license__ = "<company name>"
__version__ = "0.1"
__maintainer__ = "Maziyar Boustani"
__email__ = "maziyarb4@gmail.com"
__description__ = "Code to store all views and routes."


from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from pyzipcode import ZipCodeDatabase
from timezonefinder import TimezoneFinder
#import yfinance as yf

import os
import datetime
import urllib.request
import json
import asyncio
import threading
import multiprocessing
from multiprocessing import pool
import requests as reqs
import time

import tasks
import listen
#import face_detect
import speak


app = FastAPI(docs_url="/chsunvysgsjhsbgcaky", redoc_url=None, debug=False)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key='98b8-7yjn0s4vsn8y98n349$%3T$23r') #!secret

zcdb = ZipCodeDatabase()
tf = TimezoneFinder()
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
show_spinning_icon  = "http://localhost:8000/show_spinning_icon"
update_command_url  = "http://localhost:8000/update_command/"
empty_command_url  = "http://localhost:8000/empty_command/"
marvin_command = None # Format {'speaker': 'bot', 'content': 'test'} Marvin or You, make it None for not showing it

f = open('config.json')
config_data = json.load(f)
os.environ['OPENAI_API_KEY'] = config_data['openai_api_key']

def person_detection():
    face_detect.detect_face()

def wake_up_call():
    while True:
        if listen.wake_up_call(True) == "wake_up_call":
            reqs.post(show_spinning_icon)
            speak.say("How can I help you.")
            #time.sleep(0.5)
            reqs.post(update_command_url + 'Marvin' + '/' + "How can I help you?")
            reqs.post(show_spinning_icon)
            command = listen.take_command(False)
            print('command', command)
            reqs.post(update_command_url + 'You' + '/' + command)
            if command:
                responses = tasks.task_detector(command)
                for respons in responses:
                    speak.say(respons)
                    reqs.post(update_command_url + 'Marvin' + '/' + respons)


class Config_data(BaseModel):
    zip_code: str
    stock_tickers: str
    crypto_tickers: str
    openai_api_key: str
    

def get_weather():
    f = open('config.json')
    config_data = json.load(f)
    zip_code = 90001
    lat = 34.1
    lng = -118.2
    zip_code = config_data['zip_code']
    
    try:
        lat = zipcode.longitude
        lng = zipcode.longitude
        zipcode = zcdb[zip_code]
        time_zone = tf.timezone_at(lng=lng, lat=lat)
    except:
        time_zone = "America/Los_Angeles"

    daily_min_max_rain = []
    weather_url = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&temperature_unit=fahrenheit&timezone={time_zone}&current_weather=True&daily=temperature_2m_max,temperature_2m_min,rain_sum&timeformat=unixtime".format(lat=lat, lng=lng, time_zone=time_zone)
    response = urllib.request.urlopen(weather_url)
    data = json.loads(response.read())
    if data:
        current_weather = data['current_weather']
        current_temperature = current_weather['temperature']
        daily = data['daily']
        daily_min_max_rain = []
        for time, min_val, max_val, rain_val in zip(daily['time'], daily['temperature_2m_min'], daily['temperature_2m_max'], daily['rain_sum']):
            # change time format
            dt = datetime.datetime.fromtimestamp(time)
            time = days[dt.weekday()]
            if rain_val > 0:
                rain_val = 'Rainy'
            else:
                rain_val = ""
            daily_min_max_rain.append([time, min_val, max_val, rain_val])
    # skip today
    return daily_min_max_rain[1:]


def get_stock_price():
    f = open('config.json')
    config_data = json.load(f)
    stock_tickers = config_data["stock_tickers"]
    stock_prices = []
    for ticker in stock_tickers:
        try:
            data = yf.Ticker(ticker.upper())
            if data:
                stock_prices.append([[data.info['symbol']], int(data.info['currentPrice'])])
        except:
            pass
    return stock_prices


def get_crypto_price():
    f = open('config.json')
    config_data = json.load(f)
    crypto_tickers = config_data["crypto_tickers"]
    crypto_prices = []
    for ticker in crypto_tickers:
        coinbase_url = "https://api.coinbase.com/v2/prices/{ticker}-USD/sell".format(ticker=ticker.upper())
        try:
            response = urllib.request.urlopen(coinbase_url)
            data = json.loads(response.read())
            if data:
                crypto_prices.append([[data['data']['base']], data['data']['amount']])
        except:
            pass
    return crypto_prices


@app.get('/config')
def config(request: Request):
    # read config json file
    f = open('config.json')
    config_data = json.load(f)
    config_data['stock_tickers'] = (",").join(config_data['stock_tickers'])
    config_data['crypto_tickers'] = (",").join(config_data['crypto_tickers'])
    return templates.TemplateResponse("config.html", {"request": request,
                                                      "config_data": config_data})


@app.post('/save_config')
def save_config(request: Request, config_data: Config_data):
    if config_data:
        # check if valid zip code
        f = open('config.json')
        old_config_data = json.load(f)
        old_config_data['zip_code'] = config_data.zip_code
        old_config_data['stock_tickers'] = config_data.stock_tickers.split(",")
        old_config_data['crypto_tickers'] = config_data.crypto_tickers.split(",")
        old_config_data['openai_api_key'] = config_data.openai_api_key
        with open("config.json", "w") as outfile:
            json.dump(old_config_data, outfile)


@app.post('/update_weather')
def update_weather(request: Request):
    daily_min_max_rain = get_weather()
    return {"daily_min_max_rain": daily_min_max_rain}
    

@app.post('/update_stock_price')
def update_stock_price(request: Request):
    stock_prices = get_stock_price()
    return {"stock_prices": stock_prices}


@app.post('/update_crypto_price')
def update_crypto_price(request: Request):
    crypto_prices = get_crypto_price()
    return {"crypto_prices": crypto_prices}


@app.get("/", response_class=HTMLResponse)
@app.get("/index", response_class=HTMLResponse)
def home(request: Request):
    for p in multiprocessing.active_children():
        p.terminate()
    process1 = multiprocessing.Process(target=wake_up_call)
    #process2 = multiprocessing.Process(target=person_detection)
    process1.start()
    #process2.start()

    f = open('config.json')
    config_data = json.load(f)
    zip_code = 90001
    lat = 34.1
    lng = -118.2
    # get zip code
    zip_code = config_data['zip_code']
    
    try:
        lat = zipcode.longitude
        lng = zipcode.longitude
        zipcode = zcdb[zip_code]
        timezone = tf.timezone_at(lng=lng, lat=lat)
    except:
        timezone = "America/Los_Angeles"
    
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "time_zone": timezone,
})


@app.post("/show_spinning_icon")
def show_spinining_icon(request: Request):
    global marvin_command
    marvin_command = {'content': 'show_spinning_icon'}

@app.post("/update_command/{speaker}/{content}")
def update_command(request: Request, speaker:str, content:str):
    global marvin_command
    if speaker and content:
        marvin_command = {'content': {'speaker': speaker, 'content': content}}


@app.post("/empty_command")
def empty_command(request: Request):
    global marvin_command
    marvin_command = None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(1)
        await websocket.send_json(marvin_command)


    

    

    