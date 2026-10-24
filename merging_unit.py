"""Generate sampled-value records from simulated grid waveforms."""

from dataclasses import dataclass
from typing import Iterator

from scapy.layers.l2 import Ether

from iec61850_stack.sv_layer import SVLayer
from power_grid_sim.grid_transients import GridWaveform, simulate_transient


@dataclass(frozen=True)
class SampledValue:
    sample_count: int
    time_s: float
    ia_a: float
    ib_a: float
    ic_a: float
    va_v: float
    vb_v: float
    vc_v: float
    publisher_mac: str


def stream(waveform: GridWaveform | None = None, publisher_mac: str = "02:00:00:00:01:11") -> Iterator[SampledValue]:
    """Yield 4000-sample/s records in process; callers choose any transport."""
    source = waveform or simulate_transient()
    for count, time_s in enumerate(source.time_s):
        yield SampledValue(
            count,
            float(time_s),
            *map(float, source.hv_current_a[count]),
            *map(float, source.hv_voltage_v[count]),
            publisher_mac,
        )


def sampled_value_frame(
    sample: SampledValue,
    current_scale: float = 1000.0,
) -> Ether:
    """Encode one simulated sample into the local Scapy SV training profile.

    Currents are encoded in milliamperes and voltages in volts. The result is
    an in-memory Ethernet packet object; this function never transmits it.
    """
    if current_scale <= 0:
        raise ValueError("current_scale must be positive")
    return (
        Ether(src=sample.publisher_mac, dst="01:0c:cd:04:00:00", type=0x88BA)
        / SVLayer(
            appid=0x4000,
            smp_cnt=sample.sample_count,
            ia=round(sample.ia_a * current_scale),
            ib=round(sample.ib_a * current_scale),
            ic=round(sample.ic_a * current_scale),
            va=round(sample.va_v),
            vb=round(sample.vb_v),
            vc=round(sample.vc_v),
        )
    )
