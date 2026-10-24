"""Three-phase 132/33 kV source and transformer transient waveforms."""

from dataclasses import dataclass

import numpy as np

from config import load_substation_params

@dataclass(frozen=True)
class GridWaveform:
    time_s: np.ndarray
    hv_voltage_v: np.ndarray
    lv_voltage_v: np.ndarray
    hv_current_a: np.ndarray
    lv_current_a: np.ndarray


def simulate_transient(
    duration_s: float = 0.2,
    sample_rate_hz: int | None = None,
    frequency_hz: float | None = None,
    fault_time_s: float | None = None,
    fault_location: str = "none",
    fault_resistance_ohm: float = 2.0,
    source_resistance_ohm: float = 0.4,
    source_inductance_h: float = 0.015,
) -> GridWaveform:
    """Return instantaneous three-phase primary quantities for a simple RL fault.

    The model is a balanced Thevenin source and ideal ratio transformer. An
    internal fault adds a decaying RL current on the HV side; an external fault
    is reflected to both sides and therefore remains approximately balanced
    after per-unit normalization. It is a teaching model, not a network solver.
    """
    settings = load_substation_params()
    frequency_hz = settings["frequency_hz"] if frequency_hz is None else frequency_hz
    sample_rate_hz = settings["network"]["sample_rate_hz"] if sample_rate_hz is None else sample_rate_hz
    transformer = settings["transformer"]
    hv_kv = transformer["hv_kv_line_line"]
    lv_kv = transformer["lv_kv_line_line"]
    rating_va = transformer["rating_mva"] * 1e6
    if duration_s <= 0 or sample_rate_hz <= 0 or frequency_hz <= 0:
        raise ValueError("duration, sample rate, and frequency must be positive")
    if fault_location not in {"none", "internal", "external"}:
        raise ValueError("fault_location must be none, internal, or external")
    time = np.arange(0.0, duration_s, 1.0 / sample_rate_hz)
    phase = 2.0 * np.pi * frequency_hz * time[:, None] + np.deg2rad([0, -120, 120])
    hv_peak = hv_kv * 1000.0 * np.sqrt(2.0 / 3.0)
    lv_peak = lv_kv * 1000.0 * np.sqrt(2.0 / 3.0)
    hv_voltage = hv_peak * np.sin(phase)
    lv_voltage = lv_peak * np.sin(phase + np.deg2rad(30.0))

    rated_hv_current = rating_va / (np.sqrt(3.0) * hv_kv * 1000.0)
    rated_lv_current = rating_va / (np.sqrt(3.0) * lv_kv * 1000.0)
    hv_current = np.sqrt(2.0) * rated_hv_current * np.sin(phase - np.deg2rad(20.0))
    lv_current = np.sqrt(2.0) * rated_lv_current * np.sin(phase - np.deg2rad(20.0))

    if fault_time_s is not None and fault_location != "none":
        if fault_time_s < 0:
            raise ValueError("fault_time_s cannot be negative")
        active = time >= fault_time_s
        resistance = source_resistance_ohm + fault_resistance_ohm
        if resistance <= 0 or source_inductance_h <= 0:
            raise ValueError("fault resistance and source inductance must be positive")
        tau = source_inductance_h / resistance
        omega = 2.0 * np.pi * frequency_hz
        phase_angles = np.deg2rad([0, -120, 120])
        source_peak = hv_kv * 1000.0 / np.sqrt(3.0) * np.sqrt(2.0)
        impedance = np.hypot(resistance, omega * source_inductance_h)
        current_peak = source_peak / impedance
        current_lag = np.arctan2(omega * source_inductance_h, resistance)
        steady_state = current_peak * np.sin(
            omega * time[:, None] + phase_angles - current_lag
        )
        inception_steady = current_peak * np.sin(
            omega * fault_time_s + phase_angles - current_lag
        )
        inception_current = np.sqrt(2.0) * rated_hv_current * np.sin(
            omega * fault_time_s + phase_angles - np.deg2rad(20.0)
        )
        dc_component = (inception_current - inception_steady) * np.exp(
            -np.maximum(time - fault_time_s, 0.0)[:, None] / tau
        )
        added = np.where(active[:, None], steady_state + dc_component, 0.0)
        hv_current = hv_current + added
        if fault_location == "external":
            lv_current = lv_current + added * (hv_kv / lv_kv)

    return GridWaveform(time, hv_voltage, lv_voltage, hv_current, lv_current)
