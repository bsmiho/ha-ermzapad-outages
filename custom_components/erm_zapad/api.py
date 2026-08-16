"""Client for the public ERM Запад (ЧЕЗ) outage information service.

The official page at https://info.ermzapad.bg/webint/vok/avplan.php is JS
driven. The two POST actions below are what the page itself calls when you
enter a measurement point number (точка на измерване / ITN):

  * action=viewitn_plan  -> planned outages for the next 48 hours
  * action=viewitn       -> currently registered (planned or unplanned) outage

The service is forgiving: an unknown ITN simply returns the "no outage"
message, so responses are parsed by looking for known "nothing registered"
phrases and treating everything else as an active outage report.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import datetime

from .const import (
    API_URL,
    CURRENT_USER,
    ERROR_PREFIX,
    STATE_NO_OUTAGE,
)

NO_OUTAGE_MARKERS = (
    "няма планирани прекъсвания",
    "няма регистрирано",
    "няма данни",
    "не са регистрирани",
)

_DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{4}(?:[ Т]\d{2}:\d{2})?")


@dataclass
class OutageInfo:
    """Parsed result of a single API check."""

    state: str = STATE_NO_OUTAGE  # human readable summary (HA sensor state)
    begin: str | None = None
    end: str | None = None
    raw: str = ""

    @property
    def has_outage(self) -> bool:
        return self.state != STATE_NO_OUTAGE and not self.state.startswith(ERROR_PREFIX)


def _clean(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _parse(raw: str) -> OutageInfo:
    text = _clean(raw)
    low = text.lower()
    if any(marker in low for marker in NO_OUTAGE_MARKERS):
        return OutageInfo()
    dates = _DATE_RE.findall(text)
    info = OutageInfo(state=text[:400], raw=text)
    if dates:
        info.begin = dates[0]
        if len(dates) > 1:
            info.end = dates[1]
    return info


class ErmZapadClient:
    """Minimal urllib-based client for the avplan.php service (no external deps)."""

    def __init__(self, itn: str, session=None) -> None:
        self._itn = itn
        self._session = session  # kept for parity; urllib is used to stay dep-free

    def _post(self, action: str, user: str) -> str:
        import urllib.parse
        import urllib.request

        data = urllib.parse.urlencode(
            {
                "itn": self._itn,
                "action": action,
                "user": user,
                "lat": "",
                "lon": "",
            }
        ).encode()
        req = urllib.request.Request(
            API_URL,
            data=data,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace")

    def planned(self) -> OutageInfo:
        """Planned outages announced for the next 48h."""
        try:
            return _parse(self._post("viewitn_plan", ""))
        except Exception as exc:  # noqa: BLE001 - surface any failure to HA
            return OutageInfo(state=f"{ERROR_PREFIX}: {exc}")

    def current(self) -> OutageInfo:
        """Currently registered outage (planned or unplanned)."""
        try:
            return _parse(self._post("viewitn", CURRENT_USER))
        except Exception as exc:  # noqa: BLE001
            return OutageInfo(state=f"{ERROR_PREFIX}: {exc}")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
