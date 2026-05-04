# cockpit/services/venues_service.py
# Service layer for venue data. Delegates to CockpitStore.

from __future__ import annotations

import json
from pathlib import Path

from cockpit.database import CockpitStore
from cockpit.schemas import VenueInfo
from cockpit.services._constants import VENUE_ALIASES_FILENAME


_ALIAS_PATH = Path(__file__).with_name(VENUE_ALIASES_FILENAME)

with _ALIAS_PATH.open() as alias_file:
    VENUE_LABEL_ALIASES: dict[str, str] = json.load(alias_file)


def _alias_venue_label(label: str) -> str:
    """Return the short display label used in the cockpit venue dropdown."""
    return VENUE_LABEL_ALIASES.get(label, label)


def get_venues(db: CockpitStore) -> list[VenueInfo]:
    """Return all venues for the trading dropdown as VenueInfo objects, sorted by label."""
    raw = db.get_venues()
    field_names = tuple(VenueInfo.model_fields)
    venues: list[VenueInfo] = []
    for venue in raw:
        values = tuple(venue.values())
        venues.append(
            VenueInfo.model_validate(
                dict(
                    zip(
                        field_names,
                        (str(values[0]), _alias_venue_label(str(values[1]))),
                    )
                )
            )
        )
    return sorted(venues, key=lambda venue: venue.label)
