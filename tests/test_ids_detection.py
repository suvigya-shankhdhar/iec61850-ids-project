import unittest

from attacks.attack_1_dos import event_burst
from attacks.attack_2_spoofing import forged_trip
from attacks.attack_3_replay import replayed_trip
from attacks.attack_4_sv_manipulation import altered_sample
from ids_engine.ids_core import IDSCore


TRUSTED = {"02:00:00:00:02:21", "02:00:00:00:01:11"}


class IDSDetectionTests(unittest.TestCase):
    def setUp(self):
        self.ids = IDSCore(TRUSTED, rate_limit_per_second=50)

    def test_dos_burst_is_rate_limited(self):
        results = [self.ids.inspect_event(event) for event in event_burst()]
        self.assertTrue(any("rate_exceeded" in result.alerts for result in results))

    def test_spoofed_publisher_is_flagged(self):
        self.assertIn("publisher_mac_mismatch", self.ids.inspect_event(forged_trip()).alerts)

    def test_stale_goose_is_flagged(self):
        baseline = {
            "kind": "goose", "source_mac": "02:00:00:00:02:21",
            "timestamp_s": 1.0, "st_num": 1, "sq_num": 7,
            "time_allowed_to_live_ms": 1000, "trip": False
        }
        self.ids.inspect_event(baseline)
        self.assertIn("sequence_regression", self.ids.inspect_event(replayed_trip(1.1)).alerts)

    def test_sv_physics_inconsistency_is_flagged(self):
        result = self.ids.inspect_event(altered_sample())
        self.assertTrue({"trip_physics_mismatch", "differential_fault_trip_missing"} & set(result.alerts))

    def test_cross_correlation_flags_trip_not_matching_sv_fault_evidence(self):
        result = self.ids.inspect_signals(
            [0, 0, 1, 1, 1],
            [1, 1, 0, 0, 0],
            timestamp_s=4.0,
        )
        self.assertIn("sv_goose_correlation_low", result.alerts)


if __name__ == "__main__":
    unittest.main()
