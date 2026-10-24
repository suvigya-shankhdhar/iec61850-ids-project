"""Educational Scapy sampled-value envelope for signed 3-phase samples.

It is intentionally not presented as a complete IEC 61850-9-2 LE BER codec.
"""

from scapy.fields import IntField, ShortField, SignedIntField
from scapy.packet import Packet, bind_layers
from scapy.layers.l2 import Ether


class SVLayer(Packet):
    name = "IEC61850_SV_Training_Profile"
    fields_desc = [
        ShortField("appid", 0x4000),
        ShortField("length", None),
        ShortField("reserved1", 0),
        ShortField("reserved2", 0),
        IntField("smp_cnt", 0),
        SignedIntField("ia", 0),
        SignedIntField("ib", 0),
        SignedIntField("ic", 0),
        SignedIntField("va", 0),
        SignedIntField("vb", 0),
        SignedIntField("vc", 0),
    ]


bind_layers(Ether, SVLayer, type=0x88BA)
