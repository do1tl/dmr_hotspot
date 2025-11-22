"""Config flow for DMR Last Heard integration."""
import logging
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "dmr_last_heard"
DEFAULT_NAME = "DMR Hotspot"
DEFAULT_SCAN_INTERVAL = 30

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    
    # Füge http:// hinzu wenn nicht vorhanden
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    
    # Füge /api/ hinzu wenn nicht vorhanden
    if not host.endswith("/api/"):
        if not host.endswith("/api"):
            host = f"{host}/api/"
        else:
            host = f"{host}/"
    
    # Teste Verbindung
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(host, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise ValueError("API nicht erreichbar")
                
                data_json = await response.json()
                if not isinstance(data_json, list):
                    raise ValueError("Ungültiges API-Format")
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("Verbindungsfehler: %s", err)
            raise ValueError("Kann API nicht erreichen") from err
    
    return {"title": data[CONF_NAME], "host": host}

class DMRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DMR Last Heard."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Prüfe ob bereits konfiguriert
                await self.async_set_unique_id(info["host"])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_HOST: info["host"],
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    }
                )
            except ValueError as err:
                errors["base"] = "cannot_connect"
                _LOGGER.error("Validierung fehlgeschlagen: %s", err)
            except Exception as err:
                _LOGGER.exception("Unerwarteter Fehler: %s", err)
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default="192.168.2.10"): str,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=10, max=300)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
