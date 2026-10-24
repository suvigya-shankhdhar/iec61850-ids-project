"""GOOSE/SV metadata, publisher identity, sequence, TTL, and rate checks."""

from collections import defaultdict, deque
import math


class ProtocolInspector:
    def __init__(self, trusted_macs: set[str], rate_limit_per_second: int = 100):
        if rate_limit_per_second < 1:
            raise ValueError("rate limit must be positive")
        self.trusted_macs = {mac.lower() for mac in trusted_macs}
        self.rate_limit = rate_limit_per_second
        self._state = {}
        self._recent = defaultdict(deque)

    def inspect(self, event: dict) -> list[str]:
        required = ("source_mac", "timestamp_s", "st_num", "sq_num", "time_allowed_to_live_ms")
        missing = [key for key in required if key not in event]
        if missing:
            return ["malformed: missing " + ", ".join(missing)]
        try:
            mac = str(event["source_mac"]).lower()
            timestamp = float(event["timestamp_s"])
            st_num = int(event["st_num"])
            sq_num = int(event["sq_num"])
            ttl_ms = int(event["time_allowed_to_live_ms"])
        except (TypeError, ValueError, OverflowError):
            return ["malformed: invalid metadata type"]
        alerts = []
        if not math.isfinite(timestamp):
            return ["malformed: timestamp must be finite"]
        if mac not in self.trusted_macs:
            alerts.append("publisher_mac_mismatch")
        if timestamp < 0 or st_num < 0 or sq_num < 0 or ttl_ms <= 0:
            alerts.append("invalid_protocol_value")

        key = (mac, event.get("kind", "unknown"))
        previous = self._state.get(key)
        if previous is not None:
            old_st, old_sq, old_time, old_ttl = previous
            if timestamp < old_time:
                alerts.append("timestamp_regression")
            if st_num < old_st or (st_num == old_st and sq_num <= old_sq):
                alerts.append("sequence_regression")
            if timestamp - old_time > old_ttl / 1000.0:
                alerts.append("time_allowed_to_live_expired")
        self._state[key] = (st_num, sq_num, timestamp, ttl_ms)

        recent = self._recent[key]
        while recent and timestamp - recent[0] > 1.0:
            recent.popleft()
        recent.append(timestamp)
        if len(recent) > self.rate_limit:
            alerts.append("rate_exceeded")
        return alerts
