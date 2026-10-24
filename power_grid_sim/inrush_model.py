"""A bounded nonlinear magnetizing-inrush approximation."""

import numpy as np

from config import load_substation_params

def simulate_inrush(
    time_s: np.ndarray,
    energization_time_s: float = 0.0,
    peak_current_a: float = 800.0,
    decay_time_s: float = 0.08,
    frequency_hz: float | None = None,
    residual_flux_pu: float = 0.7,
) -> np.ndarray:
    """Generate a saturating, asymmetric three-phase inrush current waveform.

    The decaying unidirectional component models residual-flux-dependent
    saturation; the fundamental component remains at the system frequency.
    """
    frequency_hz = load_substation_params()["frequency_hz"] if frequency_hz is None else frequency_hz
    if peak_current_a < 0 or decay_time_s <= 0 or frequency_hz <= 0:
        raise ValueError("current must be nonnegative and time constants positive")
    time = np.asarray(time_s, dtype=float)
    phase = 2.0 * np.pi * frequency_hz * time[:, None] + np.deg2rad([0, -120, 120])
    elapsed = np.maximum(time - energization_time_s, 0.0)
    active = (time >= energization_time_s).astype(float)
    asymmetry = np.sign(residual_flux_pu) * peak_current_a * np.exp(-elapsed / decay_time_s)
    saturated_fundamental = peak_current_a * np.tanh(2.0 * np.sin(phase))
    second_harmonic = (
        0.35
        * min(abs(residual_flux_pu), 1.0)
        * peak_current_a
        * np.exp(-elapsed / decay_time_s)[:, None]
        * np.sin(2.0 * phase + np.sign(residual_flux_pu) * np.pi / 6.0)
    )
    return active[:, None] * (saturated_fundamental + asymmetry[:, None] + second_harmonic)
