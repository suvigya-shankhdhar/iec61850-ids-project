# IEC 61850 mapping and implementation boundary

## Intended mapping

| Function | Reference in this testbed | Protocol mapping |
| --- | --- | --- |
| Process-bus current/voltage | `SampledValue` at 4000 samples/s | IEC 61850-9-2 LE-style 80-sample/cycle stream |
| Transformer trip/status | event `trip`, `st_num`, `sq_num`, TTL | IEC 61850-8-1 GOOSE state/event metadata |
| Ethernet identifiers | EtherType `0x88BA` / `0x88B8` | Sampled Values / GOOSE |
| Process bus | VLAN 100, APPID 0x4000 / 0x0001 | Lab configuration in `config/network_config.json` |

## Decoder scope

The Scapy classes expose compact typed training envelopes and bind them to the correct EtherTypes. Their field encoding is **not** the complete standardized ASN.1 BER encoding of GOOSE or SV. They are useful for the offline teaching pipeline and must not be described as interoperable IEC 61850 implementations. Interoperability requires standardized BER parsing/encoding, the selected IEC 61850-9-2 LE profile, quality and dataset fields, configuration (SCL), VLAN/priority handling, and conformance testing.

`stNum` denotes a GOOSE state number and `sqNum` its sequence number within that state. A state change increments `stNum`; retransmissions increment `sqNum`. Receivers check publisher MAC allow-lists and elapsed time against the prior advertised timeAllowedToLive. MAC allow-lists are not cryptographic authentication; use IEC 62351 controls and managed network controls in a real system.

## Network topology

The optional Mininet definition uses separate process-bus and station-bus switches. The two MUs, 87T relay, and breaker attach to the process bus; the IDS is dual-homed; a SCADA host attaches to the station bus. It uses software endpoints only. This repository does not configure physical interfaces, bridge to an external network, or launch packet transmitters. Install/run Mininet only in an isolated Linux lab.
