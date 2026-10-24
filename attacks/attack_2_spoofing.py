"""Forged-publisher fixture for offline nuisance-trip detection."""


def forged_trip(timestamp_s: float = 1.0):
    return {
        "kind": "goose",
        "source_mac": "02:de:ad:be:ef:01",
        "timestamp_s": timestamp_s,
        "st_num": 3,
        "sq_num": 0,
        "time_allowed_to_live_ms": 1000,
        "trip": True,
    }
