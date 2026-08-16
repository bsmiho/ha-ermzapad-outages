"""Text sensors exposing the raw ERM Запад outage report per check."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import now_str
from .const import (
    ATTR_BEGIN,
    ATTR_END,
    ATTR_ITN,
    ATTR_LAST_UPDATE,
    DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add the two text sensors for this entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    itn = data["itn"]
    async_add_entities(
        [
            ErmZapadTextSensor(data["planned"], "planned", itn),
            ErmZapadTextSensor(data["current"], "current", itn),
        ]
    )


class ErmZapadTextSensor(CoordinatorEntity, SensorEntity):
    """Sensor whose state is the human-readable ERM Запад report."""

    def __init__(self, coordinator, kind: str, itn: str) -> None:
        super().__init__(coordinator)
        self._kind = kind
        self._attr_unique_id = f"{DOMAIN}_{kind}_outage_{itn}"
        self._attr_itn = itn
        self._attr_name = (
            "ERM Запад — Планирано прекъсване"
            if kind == "planned"
            else "ERM Запад — Текущо прекъсване"
        )

    @property
    def native_value(self) -> str:
        return self.coordinator.data.state

    @property
    def extra_state_attributes(self) -> dict:
        info = self.coordinator.data
        return {
            ATTR_ITN: self._attr_itn,
            ATTR_BEGIN: info.begin,
            ATTR_END: info.end,
            ATTR_LAST_UPDATE: now_str(),
        }
