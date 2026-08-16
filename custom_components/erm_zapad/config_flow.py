"""Config flow for the ERM Запад (ЧЕЗ) outages integration.

The measurement point number (точка на измерване / ITN) is entered by the
user in the UI — it is never stored in the code or shipped defaults.
"""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CURRENT_INTERVAL,
    CONF_ITN,
    CONF_PLANNED_INTERVAL,
    DEFAULT_CURRENT_INTERVAL,
    DEFAULT_PLANNED_INTERVAL,
    DOMAIN,
    MIN_CURRENT_INTERVAL,
    MIN_PLANNED_INTERVAL,
)


def _validate_itn(itn: str) -> bool:
    """The official site accepts 12 or 16 character measurement point numbers."""
    itn = itn.strip()
    return len(itn) in (12, 16)


class ErmZapadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for ERM Запад."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            itn = user_input[CONF_ITN].strip()
            if not itn:
                errors[CONF_ITN] = "required"
            elif not _validate_itn(itn):
                errors[CONF_ITN] = "invalid_itn"
            else:
                await self.async_set_unique_id(itn)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"ERM Запад ({itn})",
                    data={CONF_ITN: itn},
                    options={
                        CONF_PLANNED_INTERVAL: user_input.get(
                            CONF_PLANNED_INTERVAL, DEFAULT_PLANNED_INTERVAL
                        ),
                        CONF_CURRENT_INTERVAL: user_input.get(
                            CONF_CURRENT_INTERVAL, DEFAULT_CURRENT_INTERVAL
                        ),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ITN): str,
                vol.Optional(
                    CONF_PLANNED_INTERVAL,
                    default=DEFAULT_PLANNED_INTERVAL,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_PLANNED_INTERVAL),
                ),
                vol.Optional(
                    CONF_CURRENT_INTERVAL,
                    default=DEFAULT_CURRENT_INTERVAL,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_CURRENT_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"name": "ERM Запад (ЧЕЗ)"},
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "ErmZapadOptionsFlow":
        return ErmZapadOptionsFlow(config_entry)


class ErmZapadOptionsFlow(config_entries.OptionsFlow):
    """Options flow: change ITN and/or polling intervals."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            itn = user_input.get(CONF_ITN, self._config_entry.data[CONF_ITN]).strip()
            if not _validate_itn(itn):
                errors[CONF_ITN] = "invalid_itn"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_ITN: itn,
                        CONF_PLANNED_INTERVAL: user_input[CONF_PLANNED_INTERVAL],
                        CONF_CURRENT_INTERVAL: user_input[CONF_CURRENT_INTERVAL],
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ITN, default=self._config_entry.data[CONF_ITN]
                ): str,
                vol.Optional(
                    CONF_PLANNED_INTERVAL,
                    default=self._config_entry.options.get(
                        CONF_PLANNED_INTERVAL, DEFAULT_PLANNED_INTERVAL
                    ),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_PLANNED_INTERVAL),
                ),
                vol.Optional(
                    CONF_CURRENT_INTERVAL,
                    default=self._config_entry.options.get(
                        CONF_CURRENT_INTERVAL, DEFAULT_CURRENT_INTERVAL
                    ),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_CURRENT_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
