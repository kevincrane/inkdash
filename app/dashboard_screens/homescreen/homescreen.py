import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from os import path

import pytz
from flask import render_template
from pyowm.weatherapi25.one_call import OneCall

from app import TEMPLATE_PATH
from app.config import OWM_API_KEY, WEATHER_LON, WEATHER_LAT, CALENDAR_IDS, TIMEZONE
from app.dashboard_screens.dashboard_base import DashboardScreen
from app.dashboard_screens.homescreen.gcal_events import GCalEvents, CalendarEvent
from app.dashboard_screens.homescreen.todoist import Todoist, TodoistTask
from app.dashboard_screens.homescreen.weather import Weather
from app.dashboard_screens.render import html_to_bmp


class HomeScreen(DashboardScreen):
    """ Renders a homescreen with information for today (events, tasks, weather).

        Wrote the code myself but the formatting and style is largely copied from:
        https://github.com/speedyg0nz/MagInkDash
    """
    def __init__(self, app, static_directory, filename):
        super().__init__(app, static_directory, filename)

        self.weather = Weather(owm_api_key=OWM_API_KEY, latitude=WEATHER_LAT, longitude=WEATHER_LON)
        self.gcal_events = GCalEvents(static_directory=static_directory, calendar_ids=CALENDAR_IDS)
        self.todoist = Todoist()
        self.template_path = path.join(TEMPLATE_PATH, 'homescreen')

    @dataclass
    class HomescreenTemplateProperties:
        gcal_events: list[CalendarEvent]
        tasks: list[TodoistTask]
        current_weather: OneCall
        today: datetime

    def process_image(self, delete_interim_html=True):
        self.app.logger.info(f'Fetching next events from calendars {CALENDAR_IDS}...')
        next_events = self.gcal_events.get_next_events(20)

        self.app.logger.info(f'Fetching Todoist tasks for today & tomorrow...')
        next_tasks = self.todoist.get_next_tasks()

        self.app.logger.info('Fetching local weather from OpenWeatherMap...')
        current_weather = self.weather.get_weather()

        template_props = self.HomescreenTemplateProperties(
            gcal_events=next_events,
            tasks=next_tasks,
            current_weather=current_weather,
            today=datetime.now(tz=pytz.timezone(TIMEZONE))
        )

        self.__render_html_as_image(template_props, delete_interim_html)

    def __render_html_as_image(self, props: HomescreenTemplateProperties, delete_interim_html: bool):
        temp_html_path = f'{self.template_path}/homescreen.html'
        html_output = render_template(
            'homescreen/homescreen_template.html',
            today=props.today,
            timedelta=timedelta,
            events=props.gcal_events,
            max_events=14,
            tasks=props.tasks,
            max_tasks=14,
            weather=props.current_weather,
        )
        with open(temp_html_path, 'w') as file_out:
            file_out.write(html_output)

        html_to_bmp(html_path=temp_html_path, output_path=f'{self.static_directory}/{self.filename}')

        if delete_interim_html:
            os.remove(temp_html_path)
