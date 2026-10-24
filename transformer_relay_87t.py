"""Phasor-domain transformer differential relay model (ANSI 87T)."""

from dataclasses import dataclass

import numpy as np
from scapy.layers.l2 import Ether

from config import load_substation_params
from iec61850_stack.goose_layer import GooseLayer
from power_grid_sim.signal_processing import harmonic_ratio


@dataclass(frozen=True)
class RelayResult:
    operate: bool
    idiff_pu: float
    irest_pu: float
    second_harmonic_ratio: float
    threshold_pu: float


def ynd11_compensation_matrix() -> np.ndarray:
    """Return a sequence-domain YNd11 matrix in the project's phase convention.

    Positive sequence is rotated by -30 degrees, negative sequence by +30
    degrees, and zero sequence is removed to represent the delta winding.
    """
    a = np.exp(1j * 2.0 * np.pi / 3.0)
    sequence = np.array(
        [[1, 1, 1], [1, a, a**2], [1, a**2, a]], dtype=complex
    ) / 3.0
    phase = np.linalg.inv(sequence)
    compensation = np.diag([0.0, np.exp(-1j * np.deg2rad(30.0)), np.exp(1j * np.deg2rad(30.0))])
    return phase @ compensation @ sequence


def compensate_ynd11(lv_phasors: np.ndarray) -> np.ndarray:
    """Apply the sequence-domain YNd11 compensation matrix."""
    values = np.asarray(lv_phasors, dtype=complex)
    if values.shape != (3,):
        raise ValueError("LV input must contain three phase phasors")
    return ynd11_compensation_matrix() @ values


def differential_relay(
    hv_phasors_a: np.ndarray,
    lv_phasors_a: np.ndarray,
    rated_secondary_a: float | None = None,
    pickup_pu: float | None = None,
    slope1: float | None = None,
    slope2: float | None = None,
    breakpoint_pu: float | None = None,
    second_harmonic_ratio: float = 0.0,
    harmonic_block_ratio: float | None = None,
) -> RelayResult:
    """Evaluate a dual-slope restraint characteristic with harmonic blocking.

    Input phasors are three-element RMS secondary-current vectors in the relay
    polarity convention. YNd11 compensation applies the declared sequence
    matrix; CT wiring and saturation remain outside this simplified model.
    Verify the convention against the installed relay's settings.
    """
    configuration = load_substation_params()
    settings = configuration["protection"]
    transformer = configuration["transformer"]
    if rated_secondary_a is None:
        rated_primary_a = (
            transformer["rating_mva"] * 1e6
            / (np.sqrt(3.0) * transformer["hv_kv_line_line"] * 1000.0)
        )
        rated_secondary_a = (
            rated_primary_a
            * transformer["hv_ct_secondary_a"]
            / transformer["hv_ct_primary_a"]
        )
    pickup_pu = settings["pickup_pu"] if pickup_pu is None else pickup_pu
    slope1 = settings["slope1"] if slope1 is None else slope1
    slope2 = settings["slope2"] if slope2 is None else slope2
    breakpoint_pu = settings["slope_breakpoint_pu"] if breakpoint_pu is None else breakpoint_pu
    harmonic_block_ratio = (
        settings["second_harmonic_block_ratio"]
        if harmonic_block_ratio is None
        else harmonic_block_ratio
    )
    hv = np.asarray(hv_phasors_a, dtype=complex)
    lv = compensate_ynd11(np.asarray(lv_phasors_a, dtype=complex))
    if hv.shape != (3,) or lv.shape != (3,):
        raise ValueError("HV and LV inputs must each contain three phase phasors")
    if rated_secondary_a <= 0 or breakpoint_pu <= 0:
        raise ValueError("rated current and breakpoint must be positive")
    hv_pu = hv / rated_secondary_a
    lv_pu = lv / rated_secondary_a
    idiff = float(np.mean(np.abs(hv_pu + lv_pu)))
    irest = float(np.mean((np.abs(hv_pu) + np.abs(lv_pu)) / 2.0))
    threshold = pickup_pu + slope1 * min(irest, breakpoint_pu)
    if irest > breakpoint_pu:
        threshold += slope2 * (irest - breakpoint_pu)
    blocked = second_harmonic_ratio >= harmonic_block_ratio
    return RelayResult(not blocked and idiff > threshold, idiff, irest, second_harmonic_ratio, threshold)


def cycle_harmonic_ratio(samples: np.ndarray, sample_rate_hz: float = 4000.0) -> float:
    return harmonic_ratio(samples, sample_rate_hz)


def goose_frame(
    result: RelayResult,
    publisher_mac: str = "02:00:00:00:02:21",
    st_num: int = 1,
    sq_num: int = 0,
) -> Ether:
    """Build an in-memory GOOSE training-profile frame for relay output."""
    ttl_ms = load_substation_params()["network"]["goose_time_allowed_to_live_ms"]
    return (
        Ether(src=publisher_mac, dst="01:0c:cd:01:00:01", type=0x88B8)
        / GooseLayer(
            appid=1,
            time_allowed_to_live_ms=ttl_ms,
            st_num=st_num,
            sq_num=sq_num,
            trip=int(result.operate),
        )
    )
