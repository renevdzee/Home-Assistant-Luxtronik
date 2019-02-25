"""
Support for monitoring the state of a Luxtronik heatpump.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/sensor.luxtronik/
"""
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from . import (
    CONF_SENSORS, DATA_LUXTRONIK, DOMAIN)
from homeassistant.const import (TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['luxtronik']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SENSORS): vol.All(cv.ensure_list, [cv.string]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Luxtronik sensor."""
    lt = hass.data.get(DATA_LUXTRONIK)
    if not lt:
        return False

    sensors = config.get(CONF_SENSORS)

    entities = []
    for sensor in sensors:
        if lt.valid_sensor_id(sensor):
            entities.append(LuxtronikSensor(lt, sensor))
        else:
            _LOGGER.warning("Invalid Luxtronik ID %s", sensor)

    add_entities(entities, True)


class LuxtronikSensor(Entity):
    """Representation of a Luxtronik sensor."""

    def __init__(self, lt, sensor):
        """Initialize a new Luxtronik sensor."""
        self._luxtronik = lt
        self._sensor = sensor
        self._state = None
        self._unit = None
        self._device_class = None
        self._data = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DOMAIN}_{self._sensor}"

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        icons = {
            "celsius": "mdi:thermometer",
            "kelvin": "mdi:thermometer",
            "bar": "mdi:arrow-collapse-all",
            "kWh": "mdi:flash-circle"
            }
        return icons.get(self._data["unit"])

    @property
    def state(self):
        """Return true if the UPS is online, else False."""
        return self._state

    @property
    def device_class(self):
        """Return the class of this sensor."""
        device_classes = {
            "celsius": "temperature",
            "kelvin": "temperature",
            "pressure": "pressure"
            }
        return device_classes.get(self._data["unit"])

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        units = {
            "celsius": TEMP_CELSIUS,
            "kelvin": "K",
            "bar": "bar"
            }
        return units.get(self._data["unit"], self._data["unit"])

    def update(self):
        """Get the latest status and use it to update our sensor state."""
        self._luxtronik.update()
        data = self._luxtronik.data
        # use get() here!!!
        for category in data:
            for value in data[category]:
                if data[category][value]['id'] == self._sensor:
                    self._state = data[category][value]['value']
                    self._data = data[category][value]
