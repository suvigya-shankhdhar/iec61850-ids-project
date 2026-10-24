"""Full-cycle discrete Fourier phasor extraction at 50 Hz and 100 Hz."""

import numpy as np


def fcdft(samples: np.ndarray, frequency_hz: float, sample_rate_hz: float) -> np.ndarray:
    """Return an RMS complex phasor from exactly one cycle of real samples."""
    values = np.asarray(samples, dtype=float)
    if values.ndim == 0 or values.shape[0] < 2:
        raise ValueError("at least two samples are required")
    if frequency_hz <= 0 or sample_rate_hz <= 0:
        raise ValueError("frequencies must be positive")
    n = values.shape[0]
    sample_index = np.arange(n)
    kernel = np.exp(-2j * np.pi * frequency_hz * sample_index / sample_rate_hz)
    return (np.sqrt(2.0) / n) * np.tensordot(kernel, values, axes=(0, 0))


def harmonic_ratio(samples: np.ndarray, sample_rate_hz: float, fundamental_hz: float = 50.0) -> float:
    """Return the 2nd-harmonic to fundamental RMS ratio for one-cycle samples."""
    fundamental = np.abs(fcdft(samples, fundamental_hz, sample_rate_hz))
    second = np.abs(fcdft(samples, 2.0 * fundamental_hz, sample_rate_hz))
    if np.all(fundamental <= np.finfo(float).eps):
        return 0.0 if np.all(second <= np.finfo(float).eps) else float("inf")
    return float(np.mean(second / np.maximum(fundamental, np.finfo(float).eps)))
