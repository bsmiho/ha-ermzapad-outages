"""Constants for the ERM Запад (ЧЕЗ) outages integration."""

DOMAIN = "erm_zapad"

CONF_ITN = "itn"
CONF_PLANNED_INTERVAL = "planned_scan_minutes"
CONF_CURRENT_INTERVAL = "current_scan_minutes"

DEFAULT_PLANNED_INTERVAL = 360  # minutes (~4x per day)
DEFAULT_CURRENT_INTERVAL = 120  # minutes

MIN_PLANNED_INTERVAL = 30
MIN_CURRENT_INTERVAL = 15

# Official public endpoint used by https://info.ermzapad.bg/webint/vok/avplan.php
API_URL = "https://info.ermzapad.bg/webint/vok/avplan.php"

# Public constant user token embedded in the official page's JS for the
# "current outages by object" view.
CURRENT_USER = "282drmtn94ui5u7bom2nrr474i"

STATE_NO_OUTAGE = "Няма прекъсване"
ERROR_PREFIX = "ГРЕШКА"

ATTR_BEGIN = "begin"
ATTR_END = "end"
ATTR_DETAILS = "details"
ATTR_LAST_UPDATE = "last_update"
ATTR_ITN = "itn"
