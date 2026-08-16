"""ERM Запад (ЧЕЗ) outages integration — setup, coordinators, platforms."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import ErmZapadClient
from .const import (
    CONF_CURRENT_INTERVAL,
    CONF_ITN,
    CONF_PLANNED_INTERVAL,
    DEFAULT_CURRENT_INTERVAL,
    DEFAULT_PLANNED_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


def _entry_interval(entry: ConfigEntry, key: str, default: int) -> timedelta:
    """Interval from options (or data), falling back to the default."""
    value = entry.options.get(key) or entry.data.get(key) or default
    return timedelta(minutes=int(value))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    client = ErmZapadClient(
        entry.options.get(CONF_ITN) or entry.data[CONF_ITN]
    )

    async def _update_planned():
        return await hass.async_add_executor_job(client.planned)

    async def _update_current():
        return await hass.async_add_executor_job(client.current)

    planned_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_planned",
        update_interval=_entry_interval(
            entry, CONF_PLANNED_INTERVAL, DEFAULT_PLANNED_INTERVAL
        ),
        update_method=_update_planned,
    )
    current_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_current",
        update_interval=_entry_interval(
            entry, CONF_CURRENT_INTERVAL, DEFAULT_CURRENT_INTERVAL
        ),
        update_method=_update_current,
    )

    try:
        await planned_coordinator.async_config_entry_first_refresh()
        await current_coordinator.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001
        raise ConfigEntryNotReady(f"ERM Запад първоначална проверка неуспешна: {err}") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "planned": planned_coordinator,
        "current": current_coordinator,
        "itn": entry.data[CONF_ITN],
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Recreate coordinators/sensors when options (intervals, ITN) change."""
    await hass.config_entries.async_reload_entry(entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
