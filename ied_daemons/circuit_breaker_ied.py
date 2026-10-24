"""In-process breaker model driven by authenticated trip events."""


class CircuitBreakerIED:
    def __init__(self):
        self.closed = True
        self.last_trip = None

    def receive_trip(self, trip: bool, publisher_mac: str, trusted_macs: set[str]) -> bool:
        if publisher_mac not in trusted_macs:
            raise PermissionError(f"untrusted GOOSE publisher: {publisher_mac}")
        if trip:
            self.closed = False
            self.last_trip = publisher_mac
        return self.closed
