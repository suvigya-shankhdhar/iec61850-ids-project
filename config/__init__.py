"""Load project settings from the checked-in JSON configuration."""

import json
from pathlib import Path
from typing import Any


def load_substation_params() -> dict[str, Any]:
    path = Path(__file__).with_name("substation_params.json")
    with path.open(encoding="utf-8") as settings_file:
        settings = json.load(settings_file)
    if not isinstance(settings, dict):
        raise ValueError("substation configuration must be a JSON object")
    return settings
