# Cyber-physical attack scenarios

All four cases are represented by deterministic Python dictionaries yielded or returned by `attacks/`. These fixtures do not craft or transmit live frames, flood an interface, intercept traffic, or perform man-in-the-middle actions. They exercise the two IDS engines in process.

| Scenario | Safe fixture | Expected evidence |
| --- | --- | --- |
| DoS | Timestamped event burst | Sliding one-second publisher rate exceeds configured limit |
| Injection/spoofing | Trip from an untrusted source MAC | Publisher identity mismatch; breaker model separately rejects it |
| Replay | Previously observed GOOSE state/sequence tuple | Non-increasing `sqNum` under unchanged `stNum` |
| SV manipulation | In-process waveform helper scales magnitudes and removes its 100 Hz component; an associated physics observation records the expected fault evidence | Differential-plane and trip/physics inconsistency |

The inrush check distinguishes high second-harmonic current from an ordinary differential fault and blocks an expected trip in the educational relay model. Tests make no claims of detection probability in operational networks. A safe defense uses a disconnected virtual network, synthetic time, and no external destinations.
