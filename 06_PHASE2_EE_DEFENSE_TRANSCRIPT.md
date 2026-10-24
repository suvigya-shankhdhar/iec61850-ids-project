# Phase 2 electrical-engineering defense transcript

## Panel: What changed after Phase 1?

**Team:** The phase-one proposal identified a simple substation OT LAN with merging units, protection IEDs, SCADA/HMI, and a switch. Phase 2 keeps the project title, *Development of a Protocol-Aware Intrusion Detection System for detecting cyber attacks in IEC 61850 communication*, but replaces generic dummy payloads in the software model with calculated 132/33 kV, three-phase voltage and current samples. The current samples are at 4000 samples/s, or 80 samples per 50 Hz cycle. All scenarios remain software-in-the-loop.

## Panel: Where is the electrical engineering?

**Team:** The transformer rating is 60 MVA. From three-phase power, the rated currents are about 262.4 A at 132 kV and 1049.7 A at 33 kV. With the selected 600/1 A and 2400/1 A CTs, both relay-side currents are about 0.437 A at rated load. The RL fault model produces an AC fault component and an exponentially decaying DC offset. The inrush model adds a decaying asymmetric magnetizing component and a saturated fundamental, so its second harmonic is measurable rather than inserted as a label.

## Panel: Explain the 87T element.

**Team:** We extract full-cycle RMS phasors and compensate the LV currents using a declared -30 degree rotation for the YNd11 convention used by our test vectors. The relay calculates Idiff and Irestraint per phase, applies a pickup plus two-slope bias characteristic, and blocks for a second-harmonic ratio above the configured threshold. A real relay's polarity, phase order, CT connection, zero-sequence filtering, and characteristic must be checked against its manufacturer's documentation; this model is not an implementation prescription.

## Panel: How does the IDS know a packet is wrong?

**Team:** The protocol engine tracks source MAC, `stNum`, `sqNum`, timestamps, TTL, and event rate. The physics engine checks whether the differential point is above the restraint characteristic, whether 100 Hz energy suggests inrush, and whether the trip decision agrees with the simulated internal fault. We show both protocol and physical evidence so a syntactically valid message is not automatically trusted.

## Panel: Which attacks were demonstrated?

**Team:** We tested four deterministic in-process fixtures: event-rate burst, untrusted spoofed trip, repeated stale sequence, and SV/physics inconsistency. They are test data only: the repository does not transmit floods, inject frames, or perform interception. This lets us validate detection deterministically without touching a real network.

## Panel: Is this a standards-compliant IEC 61850 implementation?

**Team:** No. EtherTypes and key metadata map to GOOSE and SV concepts, but the small Scapy training envelopes are not complete BER-coded IEC 61850 messages and are not interoperable. The software topology is isolated and optional. The work demonstrates a cyber-physical model and IDS architecture, not certified protection, conformance, or deployment readiness.

## Suggested Phase 3 evidence

Show the equations and ratings first; plot a normal and fault waveform; show the FCDFT phasors and relay operating point; then run each offline fixture and present protocol/physics alerts. Add sensitivity tests for CT ratio/polarity, fault inception angle, restraint slopes, inrush residual flux, frame loss, and jitter. Clearly label every nonvalidated assumption and do not connect the demonstrator to operational equipment.
