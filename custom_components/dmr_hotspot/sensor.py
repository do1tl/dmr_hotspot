"""Sensor platform for DMR Last Heard."""
import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "dmr_last_heard"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DMR sensors based on a config entry."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 30)
    
    coordinator = DMRDataUpdateCoordinator(
        hass,
        host=host,
        scan_interval=scan_interval,
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    sensors = [
        DMRCallsignSensor(coordinator, entry, name),
        DMRTalkgroupSensor(coordinator, entry, name),
        DMRSourceSensor(coordinator, entry, name),
        DMRTimeSensor(coordinator, entry, name),
        DMRDurationSensor(coordinator, entry, name),
        DMRLossSensor(coordinator, entry, name),
        DMRModeSensor(coordinator, entry, name),
    ]
    
    async_add_entities(sensors)

class DMRDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching DMR data."""

    def __init__(self, hass: HomeAssistant, host: str, scan_interval: int) -> None:
        """Initialize."""
        self.host = host
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.host) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"API returned status {response.status}")
                        
                        data = await response.json()
                        
                        if not isinstance(data, list) or len(data) == 0:
                            return None
                        
                        return data[0]
                        
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

class DMRBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for DMR sensors."""

    def __init__(self, coordinator: DMRDataUpdateCoordinator, entry: ConfigEntry, name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "DMR",
            "model": "Last Heard Monitor",
        }

class DMRCallsignSensor(DMRBaseSensor):
    """Sensor for last heard callsign."""

    _attr_name = "Rufzeichen"
    _attr_icon = "mdi:account-voice"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_callsign"

    @property
    def native_value(self):
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data.get("callsign", "Keine Daten")
        return "Keine Daten"

class DMRTalkgroupSensor(DMRBaseSensor):
    """Sensor for talkgroup."""

    _attr_name = "Talkgroup"
    _attr_icon = "mdi:forum"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_talkgroup"

    @property
    def native_value(self):
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data.get("target", "Keine Daten")
        return "Keine Daten"

class DMRSourceSensor(DMRBaseSensor):
    """Sensor for source (RF/Net)."""

    _attr_name = "Quelle"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_source"

    @property
    def icon(self):
        """Return icon based on source."""
        if self.coordinator.data:
            src = self.coordinator.data.get("src", "")
            return "mdi:antenna" if src == "RF" else "mdi:web"
        return "mdi:help-circle"

    @property
    def native_value(self):
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data.get("src", "Keine Daten")
        return "Keine Daten"

class DMRTimeSensor(DMRBaseSensor):
    """Sensor for last heard time."""

    _attr_name = "Zeit"
    _attr_icon = "mdi:clock-outline"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_time"

    @property
    def native_value(self):
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data.get("time_utc", "Keine Daten")
        return "Keine Daten"

class DMRDurationSensor(DMRBaseSensor):
    """Sensor for transmission duration."""

    _attr_name = "Dauer"
    _attr_icon = "mdi:timer"
    _attr_native_unit_of_measurement = "s"
    _attr_device_class = "duration"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_duration"

    @property
    def native_value(self):
        """Return the state."""
        if self.coordinator.data:
            duration = self.coordinator.data.get("duration", "")
            if duration:
                try:
                    return float(duration)
                except (ValueError, TypeError):
                    pass
        return 0

class DMRLossSensor(DMRBaseSensor):
    """Sensor for packet loss."""

    _attr_name = "Paketverlust"
    _attr_icon = "mdi:network-strength-outline"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_loss"

    @property
    def native_value(self):
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data.get("loss", "Keine Daten")
        return "Keine Daten"

class DMRModeSensor(DMRBaseSensor):
    """Sensor for DMR mode."""

    _attr_name = "Modus"
    _attr_icon = "mdi:radio-handheld"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_mode"

    @property
    def native_value(self):
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data.get("mode", "Keine Daten")
        return "Keine Daten"
