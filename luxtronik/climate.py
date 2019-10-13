"""
Support for monitoring the state of a Luxtronik heatpump.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/sensor.luxtronik/

climate component
based on examples like
https://gist.github.com/mvn23/af99067bceb4176d13073116019da8e1
https://github.com/royduin/home-assistant-incomfort/blob/master/climate.py
"""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.climate import (ClimateDevice, PLATFORM_SCHEMA)
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_COOL,
    HVAC_MODE_HEAT_COOL, HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
    CURRENT_HVAC_HEAT, CURRENT_HVAC_COOL, CURRENT_HVAC_IDLE)
from . import (
    DATA_LUXTRONIK, DOMAIN)
from homeassistant.const import (TEMP_CELSIUS, ATTR_TEMPERATURE, PRECISION_TENTHS, PRECISION_HALVES)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['luxtronik']

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Luxtronik sensor."""
    lt = hass.data.get(DATA_LUXTRONIK)
    if not lt:
        return False

    add_entities([LuxtronicThermostat(lt)])


class LuxtronicThermostat(ClimateDevice):
    """Representation of a Luxtronic Thermostat device."""

    def __init__(self, lt):
        """Initialize the thermostat."""
        self._name = "RBE"
        self._luxtronik = lt
        self._target_temperature = None
        self._current_temperature = None
        self._VD1 = 0
        self._TBW = None
        self._MODE = ""
        self._state = HVAC_MODE_OFF
        self.update()

    @property
    def state(self):
        """Return the current state."""
        return self._state

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def hvac_modes(self):
        """List of available operation modes."""
        return [HVAC_MODE_HEAT, HVAC_MODE_HEAT_COOL, HVAC_MODE_OFF]

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        if self._state in [HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_HEAT_COOL]:
            return self._state
        return HVAC_MODE_OFF

    @property
    def hvac_action(self):
        """current HVAC action"""
        #see https://github.com/Bouni/luxtronik/blob/master/luxtronik/lut.py (ID_WEB_WP_BZ_akt) for possible values
        if self._MODE=="":
            return CURRENT_HVAC_IDLE
        elif self._MODE=="cooling":
            return CURRENT_HVAC_COOL
        elif self._MODE=="heating":
            return CURRENT_HVAC_HEAT
        else:
            return CURRENT_HVAC_HEAT

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this thermostat uses."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return PRECISION_HALVES

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        # todo ... self._luxtronic.set()?
        self._target_temperature = temperature

    def set_hvac_mode(self, hvac_mode):
        """Set hvac mode heat, heatcool, off """
        # TODO

    def update(self):
        """Get the latest data."""
        self._luxtronik.update()
        data = self._luxtronik.data
        for category in data:
            for value in data[category]:
                if data[category][value]['id'] == 'ID_WEB_RBE_RT_Soll':
                    self._target_temperature = data[category][value]['value']
                if data[category][value]['id'] == 'ID_WEB_RBE_RT_Ist':
                    self._current_temperature = data[category][value]['value']
                if data[category][value]['id'] == 'ID_WEB_VD1out':
                    self._VD1 = data[category][value]['value']
                if data[category][value]['id'] == 'ID_WEB_Temperatur_TBW':
                    self._TBW = data[category][value]['value']
                if data[category][value]['id'] == 'ID_WEB_WP_BZ_akt':
                    self._MODE = data[category][value]['value']
                if data[category][value]['id'] == 'ID_WEB_FreigabKuehl':
                    if bool(data[category][value]['value']):
                        self._state = HVAC_MODE_COOL
                    else:
                        self._state = HVAC_MODE_HEAT
        # necessary? returns "no request" when idle?
        if not bool(self._VD1):
            self._MODE = ""

