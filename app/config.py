from os import getenv

# Documentation: https://inkplate.readthedocs.io/en/latest/features.html#inkplate-10
INKPLATE_SCREEN_WIDTH = 1200
INKPLATE_SCREEN_HEIGHT = 825

# ##### Home Screen configs #####
CALENDAR_IDS = getenv('CALENDAR_IDS').split(',')
TODOIST_API_KEY = getenv('TODOIST_API_KEY')
OWM_API_KEY = getenv('OWM_API_KEY')

# From: https://openweathermap.org/find?q=berkeley%2C+us
WEATHER_LAT = 37.8716
WEATHER_LON = -122.2728
TIMEZONE = 'America/Los_Angeles'
