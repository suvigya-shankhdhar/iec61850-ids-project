# Development of a Protocol-Aware Intrusion Detection System for detecting cyber attacks in IEC 61850 communication

This repository is a software-in-the-loop, cyber-physical educational prototype for a 132/33 kV, 60 MVA YNd11 transformer substation. It connects sampled three-phase waveforms, a simplified 87T differential element, GOOSE/SV protocol metadata checks, and four deterministic IDS test scenarios.

## Project layout

- `config/`: ratings, protection settings, and virtual network addresses.
- `power_grid_sim/`: RL fault transient, inrush approximation, and FCDFT.
- `ied_daemons/`: in-process MU sample generator, relay, and breaker model.
- `iec61850_stack/`: optional Scapy training envelopes bound to GOOSE/SV EtherTypes.
- `network_topology/`: optional isolated Mininet topology.
- `attacks/`: inert deterministic fixtures; no live network attack capability.
- `ids_engine/`: protocol and grid-physics engines, fusion, and plot helper.
- `tests/`: unit and fixture-detection tests.
- `docs/`: electrical model, protocol boundary, scenarios, IDS design, verification, and defense script.

## Quick start

Use Python 3.10 or newer:

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Mininet is optional and Linux-only. `build_network()` constructs but does not start the virtual topology. No daemon in this project opens a socket or publishes Ethernet frames.

## Engineering assumptions and safety boundary

The model uses 80 samples/cycle at 50 Hz (4000 samples/s), 60 MVA, 132/33 kV, 600/1 A and 2400/1 A CTs. Transformer currents are represented as instantaneous calculated waveforms, not arbitrary payload bytes. The relay uses RMS phasors, a declared YNd11 -30 degree compensation convention, two slopes, and second-harmonic restraint. These equations are educational approximations, not a validated EMT model or deployable relay setting.

Scapy classes use correct EtherType identifiers but a compact training envelope, not full standardized ASN.1 BER encodings. Do not claim IEC 61850 conformance or interoperability. The four attack examples are data fixtures for local IDS tests and do not flood, spoof, replay onto, or intercept a network. Keep optional virtual networking disconnected from production and shared networks.

See `docs/01_ELECTRICAL_MATHEMATICAL_MODEL.md` for assumptions and `docs/05_EXECUTION_AND_VERIFICATION_GUIDE.md` for verification.
