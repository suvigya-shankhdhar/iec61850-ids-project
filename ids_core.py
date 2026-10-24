"""Combines the protocol and grid-physics detection engines."""

from dataclasses import dataclass

from ids_engine.physics_validator import PhysicsValidator
from ids_engine.protocol_inspector import ProtocolInspector


@dataclass(frozen=True)
class IDSResult:
    timestamp_s: float
    alerts: tuple[str, ...]

    @property
    def detected(self) -> bool:
        return bool(self.alerts)


class IDSCore:
    def __init__(
        self,
        trusted_macs: set[str],
        rate_limit_per_second: int = 100,
        physics_validator: PhysicsValidator | None = None,
    ):
        self.protocol = ProtocolInspector(trusted_macs, rate_limit_per_second)
        self.physics = physics_validator or PhysicsValidator()
        self.alert_log: list[IDSResult] = []

    def inspect_event(self, event: dict) -> IDSResult:
        alerts = self.protocol.inspect(event)
        if "physics" in event:
            alerts.extend(self.physics.inspect_observation(event["physics"]))
        result = IDSResult(float(event.get("timestamp_s", 0.0)), tuple(dict.fromkeys(alerts)))
        if result.detected:
            self.alert_log.append(result)
        return result

    def inspect_signals(
        self,
        sv_fault_indicator,
        goose_trip,
        timestamp_s: float,
    ) -> IDSResult:
        """Fuse a time-series correlation check into the normal IDS alert log."""
        result = IDSResult(
            float(timestamp_s),
            tuple(self.physics.inspect_trip_correlation(sv_fault_indicator, goose_trip)),
        )
        if result.detected:
            self.alert_log.append(result)
        return result
