"""Educational Scapy GOOSE envelope and decoded state fields.

This profile is for controlled laboratory parsing exercises; interoperability
requires the complete IEC 61850 ASN.1 BER encoding and conformance checks.
"""

from scapy.fields import ByteField, IntField, ShortField, StrLenField
from scapy.packet import Packet, bind_layers
from scapy.layers.l2 import Ether


class GooseLayer(Packet):
    name = "IEC61850_GOOSE_Training_Profile"
    fields_desc = [
        ShortField("appid", 1),
        ShortField("length", None),
        ShortField("reserved1", 0),
        ShortField("reserved2", 0),
        IntField("time_allowed_to_live_ms", 1000),
        IntField("st_num", 1),
        IntField("sq_num", 0),
        ByteField("test", 0),
        ByteField("trip", 0),
        StrLenField("go_id", b"87T_trip", length_from=lambda pkt: 8),
    ]


bind_layers(Ether, GooseLayer, type=0x88B8)
