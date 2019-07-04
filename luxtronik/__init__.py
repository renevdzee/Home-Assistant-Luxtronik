"""

Support for Luxtronik heatpump controllers.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/luxtronik/
"""
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.const import (CONF_HOST, CONF_PORT)
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['luxtronik==0.0.4']

_LOGGER = logging.getLogger(__name__)

CONF_SENSORS = 'sensors'
CONF_ID = 'id'
CONF_INVERT_STATE = 'invert'


DATA_LUXTRONIK = 'DATA_LT'

LUXTRONIK_PLATFORMS = ['switch', 'binary_sensor', 'sensor']
DOMAIN = 'luxtronik'

ENTITY_ID_FORMAT = DOMAIN + '.{}'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST, default=""): cv.string,
        vol.Required(CONF_PORT, default=8889): cv.port,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Luxtronik component."""
    conf = config[DOMAIN]

    host = conf.get(CONF_HOST)
    port = conf.get(CONF_PORT)

    lt = LuxtronikData(host, port)
    lt.update(no_throttle=True)

    hass.data[DATA_LUXTRONIK] = lt

    return True


class LuxtronikData(object):
    """Handle all communication with Luxtronik."""

    def __init__(self, host, port):
        """Initialize the Luxtronik connection."""
        from luxtronik import Luxtronik

        self._host = host
        self._port = port
        self._luxtronik = Luxtronik(host, port)
        self.data = None

    def valid_sensor_id(self, sensor_id):
        """Validate if configured sensor ID is in data."""
        for category in self.data:
            for value in self.data[category]:
                if self.data[category][value]['id'] == sensor_id:
                    return True
        return False

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Use the data from Luxtronik."""
        self.data = self._luxtronik.get_data()
