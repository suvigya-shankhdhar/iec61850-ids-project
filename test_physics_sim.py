import unittest

import numpy as np

from attacks.attack_4_sv_manipulation import manipulate_cycle
from ied_daemons.merging_unit import sampled_value_frame, stream
from ied_daemons.transformer_relay_87t import compensate_ynd11, differential_relay, goose_frame
from power_grid_sim.grid_transients import simulate_transient
from power_grid_sim.inrush_model import simulate_inrush
from power_grid_sim.signal_processing import fcdft, harmonic_ratio
from ids_engine.physics_validator import PhysicsValidator


class PhysicsSimulationTests(unittest.TestCase):
    def test_ynd11_compensation_aligns_declared_phase(self):
        positive_sequence = np.array([1.0, np.exp(-2j * np.pi / 3), np.exp(2j * np.pi / 3)])
        lv = positive_sequence * np.exp(1j * np.deg2rad(30))
        np.testing.assert_allclose(compensate_ynd11(lv), positive_sequence, atol=1e-12)

    def test_dual_slope_relay_operates_for_internal_differential(self):
        result = differential_relay(np.array([1.5] * 3), np.array([0.0] * 3))
        self.assertTrue(result.operate)
        self.assertGreater(result.idiff_pu, result.threshold_pu)

    def test_harmonic_blocking(self):
        blocked = differential_relay(
            np.array([2.0] * 3), np.zeros(3), second_harmonic_ratio=0.2
        )
        self.assertFalse(blocked.operate)

    def test_fcdft_recovers_rms_phasor_and_second_harmonic(self):
        rate = 4000
        t = np.arange(80) / rate
        signal = 10 * np.sqrt(2) * np.sin(2 * np.pi * 50 * t + 0.2)
        self.assertAlmostEqual(abs(fcdft(signal, 50, rate)), 10.0, places=10)
        mixed = signal + 3 * np.sqrt(2) * np.sin(2 * np.pi * 100 * t)
        self.assertAlmostEqual(harmonic_ratio(mixed, rate), 0.3, places=10)

    def test_grid_transient_has_three_phase_currents_and_fault_response(self):
        normal = simulate_transient(duration_s=0.1)
        fault = simulate_transient(duration_s=0.1, fault_time_s=0.04, fault_location="internal")
        self.assertEqual(normal.hv_current_a.shape, (400, 3))
        self.assertGreater(np.max(np.abs(fault.hv_current_a[200:])), np.max(np.abs(normal.hv_current_a)))

    def test_inrush_has_second_harmonic_and_physics_engine_detects_it(self):
        samples = simulate_inrush(np.arange(80) / 4000)
        self.assertGreater(harmonic_ratio(samples[:, 0], 4000), 0.15)
        self.assertIn("inrush_harmonic_present", PhysicsValidator().inspect_cycle(samples))

    def test_sv_fixture_removes_second_harmonic_and_scales_magnitudes(self):
        rate = 4000
        time = np.arange(80) / rate
        base = np.column_stack([
            np.sin(2 * np.pi * 50 * time) + 0.4 * np.sin(2 * np.pi * 100 * time + phase)
            for phase in (0, -2 * np.pi / 3, 2 * np.pi / 3)
        ])
        altered = manipulate_cycle(base, rate, magnitude_scale=0.5)
        self.assertLess(harmonic_ratio(altered[:, 0], rate), harmonic_ratio(base[:, 0], rate))
        self.assertLess(np.max(np.abs(altered)), 0.5 * np.max(np.abs(base)))

    def test_simulated_samples_map_to_goose_and_sv_training_frames(self):
        sample = next(stream(simulate_transient(duration_s=0.001)))
        sv_packet = sampled_value_frame(sample)
        self.assertEqual(sv_packet.type, 0x88BA)
        self.assertEqual(sv_packet.payload.smp_cnt, sample.sample_count)
        relay_result = differential_relay(np.ones(3), np.zeros(3))
        goose_packet = goose_frame(relay_result)
        self.assertEqual(goose_packet.type, 0x88B8)
        self.assertEqual(goose_packet.payload.trip, int(relay_result.operate))


if __name__ == "__main__":
    unittest.main()
