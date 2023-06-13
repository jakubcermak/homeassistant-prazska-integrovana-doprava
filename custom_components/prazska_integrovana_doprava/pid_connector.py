import datetime
import logging
import dateutil.parser
from datetime import date, datetime
import aiohttp
import asyncio

import requests

_LOGGER = logging.getLogger(__name__)


class PidException(Exception):
    "Raised when something fails"

    def __init__(self, message) -> None:
        self.message = message


class PidConnection:
    def __init__(
        self, stop_from, stop_to, linenumber, scheduled, predicted, delay_available
    ) -> None:
        self.stop_from = stop_from
        self.stop_to = stop_to
        self.scheduled = scheduled
        self.predicted = predicted
        self.delay_available = delay_available
        self.linenumber = linenumber


class PidConnector:
    apiurl = "https://api.golemio.cz/v2/pid/departureboards?ids=U2223Z2&ids=U2223Z1&ids=U2259Z1&ids=U2259Z2&minutesAfter=600&limit=5"
    __cache: list[PidConnection]
    __cache_date: datetime

    def __init__(self, apikey) -> None:
        self._apikey = apikey
        self._apiheaders = {"X-Access-Token": apikey}
        self._bus_stops = {}
        self.__cache = None
        self.__cache_date = None

    def __read_departure(self, data) -> PidConnection:
        return PidConnection(
            self._bus_stops[data["stop"]["id"]],
            data["trip"]["headsign"],
            data["route"]["short_name"],
            dateutil.parser.parse(data["departure_timestamp"]["scheduled"]),
            dateutil.parser.parse(data["departure_timestamp"]["predicted"]),
            data["delay"]["is_available"],
        )

    def __is_cache_valid(self) -> bool:
        return (
            (self.__cache is not None)
            and (self.__cache_date is not None)
            and (datetime.now() - self.__cache_date).total_seconds() < 60
        )

    def get_timetable(self) -> list[PidConnection]:
        if self.__is_cache_valid():
            _LOGGER.debug("Reading data from cache")
            return self.__cache

        _LOGGER.info("Reading data from Golemio API")
        response = requests.get(self.apiurl, headers=self._apiheaders, timeout=20)
        data = response.json()
        self._bus_stops = {
            s["stop_id"]: (s["stop_name"] + " (" + s["platform_code"] + ")")
            for s in data["stops"]
        }
        _LOGGER.debug("Got stops from API: %s", self._bus_stops)

        departures = [self.__read_departure(d) for d in data["departures"]]
        _LOGGER.debug("Got departures from API: %s", departures)

        self.__cache = departures
        self.__cache_date = datetime.now()

        return departures

    def get_stops(self):
        _LOGGER.debug("loading all PID stops")
        response = requests.get(
            "https://api.golemio.cz/v2/gtfs/stops", headers=self._apiheaders, timeout=20
        )
        if response.status_code >= 400:
            _LOGGER.error("failed to get PID stops: %s", response._content)
            raise PidException(response.reason)
        data = response.json()
        result = {}
        for stop in data["features"]:
            p = stop["properties"]
            if not p["stop_name"] in result.keys():
                result.update({p["stop_name"]: []})
            result[p["stop_name"]].append(p["stop_id"])
        return result
