# Execution and verification

## Requirements

- Python 3.10 or newer
- `pip install -r requirements.txt`
- Mininet is optional, requires Linux, and is only needed to instantiate the isolated topology.

## Run verification

From this directory:

```text
python -m unittest discover -s tests -v
```

The tests cover RMS FCDFT extraction, second-harmonic measurement, the declared YNd11 compensation convention, dual-slope operation, synthetic fault response, and detection of all four deterministic attack fixtures.

## Run a waveform example

```python
from power_grid_sim.grid_transients import simulate_transient
from ids_engine.visualizer import plot_snapshot

waveform = simulate_transient(duration_s=0.2, fault_time_s=0.08, fault_location="internal")
figure = plot_snapshot(waveform.time_s, waveform.hv_current_a, [1.2], [0.2], ["internal fault"])
figure.savefig("transient.png")
```

For an isolated Mininet setup on Linux, import `build_network()` from `network_topology.substation_mininet`; the function builds but does not start the network. The simulation modules do not open sockets or send frames. Do not connect the teaching topology to a production or shared network.

## Reproducibility

Record config values, Python/package versions, fault start and resistance, sampled window, and exact fixture used in project results. The simple RL model and IEC training envelopes are not substitutes for validated EMT models or IEC 61850 conformance tools.
