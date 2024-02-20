from dataclasses import dataclass
from datetime import datetime, timedelta, date

import emoji
import pytz
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar

from app.config import TIMEZONE

GCAL_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
GCAL_CREDENTIALS_FILE = 'gcal_credentials.json'
GCAL_CLIENT_TOKEN = 'gcal_token.pickle'
tz = pytz.timezone(TIMEZONE)


@dataclass
class CalendarEvent:
    start_time: datetime
    summary: str
    calendar_id: str


class GCalEvents:
    def __init__(self, static_directory: str, calendar_ids: list):
        self._static_directory = static_directory
        self._calendar_ids = calendar_ids
        self._calendar = self.__auth_credentials()

    def __auth_credentials(self):
        return GoogleCalendar(
            read_only=True,
            credentials_path=f'{self._static_directory}/{GCAL_CREDENTIALS_FILE}',
            token_path=f'{self._static_directory}/{GCAL_CLIENT_TOKEN}'
        )

    def get_next_events(self, num_events=10) -> list[CalendarEvent]:
        """ Fetches the next num_events from Google Calendar; concatenates events from all calendars
            and returns them in order of start time. Any event that has completed already will not
            be included in the final result.
        """
        all_events = []

        now = datetime.now(tz=tz)
        for cal_id in self._calendar_ids:
            time_max = now + timedelta(days=7)

            events = list(self._calendar.get_events(
                calendar_id=cal_id,
                time_min=now,
                time_max=time_max,
                order_by='startTime',
                single_events=True))
            for event in events:
                all_events.extend(self.__process_event(event, cal_id, now))

        # Sort the combined list of events by start time and return the first N
        all_events.sort(key=lambda e: e.start_time)
        return all_events[:num_events]

    def __process_event(self, event: Event, calendar_id: str, now: datetime) -> list[CalendarEvent]:
        """ Processes an event, handling single and multi-day logic.
            Returns a list of tuples containing the start time of the event, the event summary, and
            the calendar id of the event
        """
        events_list = []

        # Strip emojis from event titles
        summary = emoji.replace_emoji(event.summary).strip()

        if not self.__is_allday_event(event):
            # Return events with specific start/end times (one-day)
            event_time = event.start.astimezone(tz=tz)
            if not self.__is_event_complete(event.end, now):
                events_list.append(CalendarEvent(event_time, summary, calendar_id))
        else:
            # Split all-day events into one day-long event per day
            num_days = (event.end - event.start).days
            events_list = []
            for i in range(num_days):
                # Create a new event for 00:00 on each day of an all-day event
                next_date = event.start + timedelta(days=i)
                event_start_time = tz.localize(datetime.combine(next_date, datetime.min.time()))
                event_end_time = tz.localize(datetime.combine(next_date, datetime.max.time()))
                if not self.__is_event_complete(event_end_time, now):
                    events_list.append(CalendarEvent(event_start_time, summary, calendar_id))
        return events_list

    @staticmethod
    def __is_allday_event(event: Event) -> bool:
        return isinstance(event.start, date) and not isinstance(event.start, datetime)

    @staticmethod
    def __is_event_complete(event_end_time: datetime, now: datetime) -> bool:
        return event_end_time < now
