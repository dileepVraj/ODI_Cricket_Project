# cockpit/services/_constants.py
# Domain constants for the cockpit service layer.
# Registered as a literal source with the compliance bouncer via
# _iter_manifest_files in core/utils/bouncer/_shared.py.

from __future__ import annotations

import re
from typing import Literal

# -- Format scope -------------------------------------------------------------

HistoryFormatScope = Literal["single", "all"]

SCOPE_SINGLE: Literal["single"] = "single"
SCOPE_ALL: Literal["all"] = "all"

# -- Trade statuses -----------------------------------------------------------

STATUS_SETTLED: str = "SETTLED"
STATUS_VOID: str = "VOID"
DEFAULT_HISTORY_STATUSES: tuple[str, ...] = (STATUS_SETTLED, STATUS_VOID)

# -- Display labels -----------------------------------------------------------

LABEL_ODI: str = "ODI"
LABEL_IPL: str = "IPL"

# -- Date range preset keys ---------------------------------------------------

RANGE_CUSTOM: str = "custom"
RANGE_7D: str = "7d"
RANGE_15D: str = "15d"
RANGE_30D: str = "30d"
RANGE_3M: str = "3m"
RANGE_6M: str = "6m"
RANGE_12M: str = "12m"

# -- Date range units and day counts ------------------------------------------

UNIT_DAYS: str = "d"
DAYS_7: int = 7

# -- SQL ordering -------------------------------------------------------------

ORDER_DESC: str = "DESC"

# -- Regex patterns -----------------------------------------------------------

RELATIVE_RANGE_PATTERN_STR: str = r"^(\d+)([dm])$"
RELATIVE_RANGE_PATTERN: re.Pattern[str] = re.compile(RELATIVE_RANGE_PATTERN_STR)

# -- Venue data ---------------------------------------------------------------

VENUE_ALIASES_FILENAME: str = "venue_aliases.json"

# -- ValueError message fragments (registered so the bouncer allows them in
#    scanned service files -- do not remove or rename these constants) ---------

_ERR_FORMAT_REQUIRED: str = "format is required when format_scope is single"
_ERR_UNKNOWN_FORMAT_PREFIX: str = "Unknown history format: "
_ERR_UNKNOWN_FORMAT_SUFFIX: str = ". Available: "
_ERR_DATES_REQUIRE_CUSTOM: str = "date_from and date_to require date_range=custom"
_ERR_CUSTOM_DATES_REQUIRED: str = "Both date_from and date_to are required for custom ranges"
_ERR_DATE_ORDER: str = "date_from must be on or before date_to"
_ERR_DATES_ONLY_CUSTOM: str = "date_from and date_to are only allowed with date_range=custom"
_ERR_UNSUPPORTED_RANGE_PREFIX: str = "Unsupported date range: "
