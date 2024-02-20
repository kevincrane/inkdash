from datetime import datetime

import pytz
from pyowm import OWM
from pyowm.weatherapi25 import one_call

from app.config import TIMEZONE


class Weather:
    """ Pulls from OpenWeatherMap; requires a OneCall subscription (should be free with limited
        usage: https://home.openweathermap.org/subscriptions
    """
    def __init__(self, owm_api_key, latitude, longitude):
        self._owm = OWM(owm_api_key)
        self._weather_manager = self._owm.weather_manager()
        self._latitude = latitude
        self._longtitude = longitude

    def get_weather(self) -> one_call.OneCall:
        """ Make an API request to the OpenWeatherMap OneCall API and return the aggregated weather
            forecast
        """
        return self._weather_manager.one_call(lat=self._latitude, lon=self._longtitude,
                                              units='imperial', exclude='minutely,alerts')

    @staticmethod
    def get_time_of_day_str(forecast: one_call.OneCall) -> str:
        """ Return 'day' or 'night', depending on the current time of day and sunset; used when
            rendering the Weather Icons with time-of-day specific icons.
        """
        now_sec = datetime.now(pytz.timezone(TIMEZONE)).timestamp()
        is_day = forecast.forecast_daily[0].srise_time <= now_sec <= forecast.forecast_daily[0].sset_time
        return 'day' if is_day else 'night'
