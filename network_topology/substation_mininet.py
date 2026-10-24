"""Isolated Mininet topology; requires Linux and Mininet to run."""

try:
    from mininet.net import Mininet
    from mininet.topo import Topo
except ImportError as exc:
    raise ImportError("Install Mininet on a Linux host to use this topology") from exc


class SubstationTopology(Topo):
    def build(self):
        process_bus = self.addSwitch("s_process")
        station_bus = self.addSwitch("s_station")
        nodes = {
            "mu_hv": ("10.0.0.11", "02:00:00:00:01:11"),
            "mu_lv": ("10.0.0.12", "02:00:00:00:01:12"),
            "relay": ("10.0.0.21", "02:00:00:00:02:21"),
            "breaker": ("10.0.0.31", "02:00:00:00:03:31"),
        }
        for name, (ip, mac) in nodes.items():
            host = self.addHost(name, ip=ip + "/24", mac=mac)
            self.addLink(host, process_bus)
        ids = self.addHost("ids", ip="10.0.0.41/24", mac="02:00:00:00:04:41")
        self.addLink(ids, process_bus)
        self.addLink(ids, station_bus)
        scada = self.addHost("scada", ip="10.0.1.51/24", mac="02:00:00:00:05:51")
        self.addLink(scada, station_bus)


def build_network():
    """Build (but do not start) the isolated educational test network."""
    return Mininet(topo=SubstationTopology(), controller=None, autoSetMacs=False)


topos = {"substation": SubstationTopology}
