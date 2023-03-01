# Code to list all tasks functions
import python_weather
from datetime import datetime
import asyncio
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import wikipedia

import gpt


def _find_loc_from_string(string):
    return ""

async def getweather(city):
  # declare the client. format defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(format=python_weather.IMPERIAL) as client:
    # fetch a weather forecast from a city
    weather = await client.get(city)

    temperature = weather.current.temperature
    description = weather.current.description

    return temperature, description

def date_time(command):
    locations = _find_loc_from_string(command)
    city = "Los Angeles"
    if locations:
        # if city exists between locations
        if locations[0]['entity_group'] == 'CITY':
            city = locations[0]['word']
    geolocator = Nominatim(user_agent="geoapiExercises")
    coords = geolocator.geocode(city)
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lng=coords.longitude, lat=coords.latitude)
    tz = pytz.timezone(timezone)
    datetime_city = datetime.now(tz)
    return ["Current time in {city} is {time}".format(city=city, time=datetime_city.strftime("%H:%M %p"))]


def weather(command):
    locations = _find_loc_from_string(command)
    weather_condition_per_city = []
    # default city for weather is Los Angeles
    city = "Los Angeles"
    if locations:
        # if city exists between locations
        if locations[0]['entity_group'] == 'CITY':
            city = locations[0]['word']
    temperature, description = asyncio.run(getweather(city))
    weather_condition_per_city.append("Temperature in {city} is {temperature} degree fahrenheit and is {description}.".format(city=city,
                                                                                                                    temperature=temperature,
                                                                                                                    description=description))
    
    return weather_condition_per_city



def wikipedia_search(keyword):
    try:
        return [wikipedia.page(keyword, auto_suggest=False).summary]
    except:
        found_serach = wikipedia.search(keyword)
        if found_search:
            return [wikipedia.page(found_serach[0], auto_suggest=False).summary]
    return ["Sorry I cannot help with this."]



def task_detector(command):
    """
    Detect what task to call based on input command.
    Examples:
    What time is in Tehran --> date_time("tehran")
    What time is in LA --> date_time("LA")

    How is weather in NY --> weather("NY")
    What is temperature in LA --> weather("LA")

    Tell me more about Elon --> wikipedia("Elon")
    Who is Barak Obama --> wikipedia("Barak Obama")
    """
    outputs = []
    prompt = gpt.detect_task_prompt.format(user_input=command)
    gpt_output = gpt.run_gpt(prompt)
    if gpt_output:
        gpt_output = gpt_output.lower()
        if "date" in gpt_output or "time" in gpt_output:
            outputs += date_time(command)
        elif "weather" in gpt_output or "temperature" in gpt_output:
            outputs += weather(command)
        else:
            outputs += ['ask gpt']

    return outputs
