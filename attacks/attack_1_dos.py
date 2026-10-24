"""In-process burst fixture for rate-detection tests; does not transmit frames."""


def event_burst(count: int = 120, interval_s: float = 0.001):
    for index in range(count):
        yield {
            "kind": "goose",
            "source_mac": "02:00:00:00:02:21",
            "timestamp_s": index * interval_s,
            "st_num": 1,
            "sq_num": index,
            "time_allowed_to_live_ms": 1000,
            "trip": False,
        }
