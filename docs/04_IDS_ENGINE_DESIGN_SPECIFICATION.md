# IDS engine design

## Engine 1: protocol state and timing

`ProtocolInspector` checks required metadata, nonnegative sequence/state values, positive TTL, trusted source MAC, timestamp monotonicity, increasing `sqNum` within a state, and a per-publisher event rate. It reports anomalies as stable alert strings rather than silently normalizing malformed data. `timeAllowedToLive` is compared to the elapsed time from the prior event; it is not a substitute for synchronized clocks or a complete GOOSE retransmission state machine.

## Engine 2: grid physics

`PhysicsValidator` calculates Idiff and Irestraint from three-phase phasor vectors, applies the configured dual-slope threshold, checks 100 Hz/50 Hz ratio and compares expected trip behavior with reported GOOSE trip and internal-fault indicators. `inspect_cycle` performs a full-cycle spectral check on three sampled current channels. `inspect_signals` in the IDS core checks the correlation of a derived SV fault indicator with the GOOSE trip time series. Engineering limits are illustrative values from configuration and require calibration for a real transformer and relay.

## Fusion and logs

`IDSCore.inspect_event` returns a timestamped immutable result, stores only non-empty alerts, and deduplicates repeated alert strings per event. The caller owns input acquisition, clock synchronization, retention policy, access controls, and alert forwarding. No inference is made from missing packets as proof of a specific attack.

## Limits

This prototype is not certified protection equipment and cannot replace a relay, process-bus implementation, packet capture sensor, cryptographic authentication, or safety engineering. Production use would need loss/jitter modeling, clock-quality validation, CT saturation and fault studies, settings coordination, false-positive characterization, signed configuration, and independent test evidence.
