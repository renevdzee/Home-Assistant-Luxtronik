"""
Support for monitoring the state of a Luxtronik heatpump.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/sensor.luxtronik/
"""
import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    BinarySensorDevice, PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv
from . import (
    CONF_SENSORS, CONF_ID, DATA_LUXTRONIK, DOMAIN, ENTITY_ID_FORMAT,
    CONF_INVERT_STATE)
from homeassistant.const import (CONF_FRIENDLY_NAME)
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['luxtronik']

DEFAULT_DEVICE_CLASS = "binary_sensor"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SENSORS): vol.All(cv.ensure_list, [
        {vol.Required(CONF_ID): cv.string,
         vol.Optional(CONF_FRIENDLY_NAME, default=""): cv.string,
         vol.Optional(CONF_INVERT_STATE, default=False): cv.boolean}
    ])
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Luxtronik binary sensor."""
    lt = hass.data.get(DATA_LUXTRONIK)
    if not lt:
        return False

    sensors = config.get(CONF_SENSORS)

    entities = []
    for sensor in sensors:
        if lt.valid_sensor_id(sensor["id"]):
            entities.append(LuxtronikBinarySensor(lt, sensor))
        else:
            _LOGGER.warning(f"Invalid Luxtronik ID %s", sensor["id"])

    add_entities(entities, True)


class LuxtronikBinarySensor(BinarySensorDevice):
    """Representation of a Luxtronik binary sensor."""

    def __init__(self, lt, sensor):
        """Initialize a new Luxtronik binary sensor."""
        self._luxtronik = lt
        self._sensor = sensor["id"]
        self._name = sensor["friendly_name"]
        self._invert = sensor["invert"]
        self._state = None
        self._device_class = None

    @property
    def entity_id(self):
        """Return the entity_id of the sensor."""
        if self._name:
            return ENTITY_ID_FORMAT.format(slugify(self._name))
        else:
            return ENTITY_ID_FORMAT.format(slugify(self._sensor))

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self.is_on:
            return "mdi:check-circle-outline"
        else:
            return "mdi:circle-outline"

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._name:
            return self._name
        else:
            return ENTITY_ID_FORMAT.format(slugify(self._sensor))

    @property
    def is_on(self):
        """Return true if binary sensor is on."""
        if self._invert:
            return not self._state
        else:
            return self._state

    @property
    def device_class(self):
        """Return the dvice class."""
        return DEFAULT_DEVICE_CLASS

    def update(self):
        """Get the latest status and use it to update our sensor state."""
        self._luxtronik.update()
        data = self._luxtronik.data
        # use get() here!!!
        for category in data:
            for value in data[category]:
                if data[category][value]['id'] == self._sensor:
                    self._state = data[category][value]['value']
