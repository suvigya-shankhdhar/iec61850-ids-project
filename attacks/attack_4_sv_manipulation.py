"""Physics-observation fixture for offline SV alteration detection."""

import numpy as np

from power_grid_sim.signal_processing import fcdft


def manipulate_cycle(currents: np.ndarray, sample_rate_hz: float = 4000.0, magnitude_scale: float = 0.5):
    """Return scaled samples with the measured 100 Hz component removed."""
    values = np.asarray(currents, dtype=float)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError("currents must have shape (samples, 3)")
    if not 0.0 <= magnitude_scale <= 1.0:
        raise ValueError("magnitude_scale must be between zero and one")
    index = np.arange(values.shape[0])
    time_s = index / sample_rate_hz
    harmonic = np.empty_like(values)
    for phase in range(3):
        phasor = fcdft(values[:, phase], 100.0, sample_rate_hz)
        harmonic[:, phase] = np.sqrt(2.0) * np.real(
            phasor * np.exp(2j * np.pi * 100.0 * time_s)
        )
    return (values - harmonic) * magnitude_scale

def altered_sample(timestamp_s: float = 3.0):
    return {
        "kind": "sv",
        "source_mac": "02:00:00:00:01:11",
        "timestamp_s": timestamp_s,
        "st_num": 1,
        "sq_num": 12000,
        "time_allowed_to_live_ms": 1000,
        "physics": {
            "idiff_pu": 0.92,
            "irest_pu": 0.18,
            "second_harmonic_ratio": 0.01,
            "goose_trip": False,
            "internal_fault": True
        }
    }
