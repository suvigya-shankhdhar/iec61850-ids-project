"""Differential-plane, inrush-harmonic, and trip/fault consistency checks."""

import math

import numpy as np

from config import load_substation_params


class PhysicsValidator:
    def __init__(
        self,
        pickup_pu: float | None = None,
        slope1: float | None = None,
        slope2: float | None = None,
        breakpoint_pu: float | None = None,
        harmonic_block_ratio: float | None = None,
    ):
        settings = load_substation_params()["protection"]
        self.pickup = settings["pickup_pu"] if pickup_pu is None else pickup_pu
        self.slope1 = settings["slope1"] if slope1 is None else slope1
        self.slope2 = settings["slope2"] if slope2 is None else slope2
        self.breakpoint = settings["slope_breakpoint_pu"] if breakpoint_pu is None else breakpoint_pu
        self.harmonic_block_ratio = (
            settings["second_harmonic_block_ratio"]
            if harmonic_block_ratio is None
            else harmonic_block_ratio
        )

    @staticmethod
    def differential_metrics(hv: np.ndarray, lv: np.ndarray) -> tuple[float, float]:
        hv_array = np.asarray(hv, dtype=complex)
        lv_array = np.asarray(lv, dtype=complex)
        if hv_array.shape != lv_array.shape or hv_array.size == 0:
            raise ValueError("current phasor arrays must have matching nonempty shapes")
        return (
            float(np.mean(np.abs(hv_array + lv_array))),
            float(np.mean((np.abs(hv_array) + np.abs(lv_array)) / 2.0)),
        )

    def inspect_observation(self, observation: dict) -> list[str]:
        required = ("idiff_pu", "irest_pu", "second_harmonic_ratio", "goose_trip", "internal_fault")
        if any(key not in observation for key in required):
            return ["physics_observation_incomplete"]
        idiff = float(observation["idiff_pu"])
        irest = float(observation["irest_pu"])
        harmonic = float(observation["second_harmonic_ratio"])
        if not all(math.isfinite(value) for value in (idiff, irest, harmonic)):
            return ["physics_observation_invalid"]
        if min(idiff, irest, harmonic) < 0:
            return ["physics_observation_invalid"]
        threshold = self.pickup + self.slope1 * min(irest, self.breakpoint)
        if irest > self.breakpoint:
            threshold += self.slope2 * (irest - self.breakpoint)
        expected_trip = idiff > threshold and harmonic < self.harmonic_block_ratio
        alerts = []
        if expected_trip != bool(observation["goose_trip"]):
            alerts.append("trip_physics_mismatch")
        if harmonic >= self.harmonic_block_ratio and bool(observation["goose_trip"]):
            alerts.append("inrush_harmonic_trip_inconsistency")
        if bool(observation["internal_fault"]) and idiff > threshold and not bool(observation["goose_trip"]):
            alerts.append("differential_fault_trip_missing")
        return alerts

    def inspect_cycle(self, currents: np.ndarray, sample_rate_hz: float = 4000.0) -> list[str]:
        """Check a full-cycle three-phase waveform for excessive 2nd harmonic."""
        samples = np.asarray(currents, dtype=float)
        if samples.ndim != 2 or samples.shape[1] != 3 or samples.shape[0] < 4:
            raise ValueError("currents must have shape (samples, 3)")
        n = samples.shape[0]
        index = np.arange(n)
        fundamental = np.abs(np.sqrt(2) / n * np.exp(-2j * np.pi * 50 * index / sample_rate_hz) @ samples)
        second = np.abs(np.sqrt(2) / n * np.exp(-2j * np.pi * 100 * index / sample_rate_hz) @ samples)
        ratio = np.mean(second / np.maximum(fundamental, np.finfo(float).eps))
        return ["inrush_harmonic_present"] if ratio >= self.harmonic_block_ratio else []

    @staticmethod
    def inspect_trip_correlation(
        sv_fault_indicator: np.ndarray,
        goose_trip: np.ndarray,
        minimum_correlation: float = 0.7,
    ) -> list[str]:
        """Check zero-lag correlation between SV-derived fault and GOOSE trip series."""
        fault = np.asarray(sv_fault_indicator, dtype=float)
        trip = np.asarray(goose_trip, dtype=float)
        if fault.ndim != 1 or trip.ndim != 1 or fault.shape != trip.shape or fault.size < 2:
            raise ValueError("fault and trip series must be matching one-dimensional arrays")
        if not 0.0 <= minimum_correlation <= 1.0:
            raise ValueError("minimum_correlation must be between zero and one")
        if np.std(fault) == 0 or np.std(trip) == 0:
            return ["sv_goose_correlation_unobservable"]
        correlation = float(np.corrcoef(fault, trip)[0, 1])
        return ["sv_goose_correlation_low"] if correlation < minimum_correlation else []
