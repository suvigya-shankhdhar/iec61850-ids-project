"""Stale-message fixture for replay detection; no packet capture or injection."""


def replayed_trip(timestamp_s: float = 2.0):
    return {
        "kind": "goose",
        "source_mac": "02:00:00:00:02:21",
        "timestamp_s": timestamp_s,
        "st_num": 1,
        "sq_num": 0,
        "time_allowed_to_live_ms": 1000,
        "trip": False,
    }
