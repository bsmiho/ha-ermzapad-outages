"""Binary sensors: ON while an outage is registered (planned / current)."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import now_str
from .const import (
    ATTR_BEGIN,
    ATTR_DETAILS,
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
    """Add the two binary sensors for this entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    itn = data["itn"]
    async_add_entities(
        [
            ErmZapadBinarySensor(data["planned"], "planned", itn),
            ErmZapadBinarySensor(data["current"], "current", itn),
        ]
    )


class ErmZapadBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """ON when an outage (planned or currently registered) exists."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, kind: str, itn: str) -> None:
        super().__init__(coordinator)
        self._kind = kind
        self._attr_unique_id = f"{DOMAIN}_{kind}_outage_flag_{itn}"
        self._attr_itn = itn
        self._attr_name = (
            "ERM Запад — Планирано прекъсване (сигнал)"
            if kind == "planned"
            else "ERM Запад — Текущо прекъсване (сигнал)"
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.has_outage

    @property
    def extra_state_attributes(self) -> dict:
        info = self.coordinator.data
        return {
            ATTR_ITN: self._attr_itn,
            ATTR_BEGIN: info.begin,
            ATTR_END: info.end,
            ATTR_DETAILS: info.state,
            ATTR_LAST_UPDATE: now_str(),
        }
