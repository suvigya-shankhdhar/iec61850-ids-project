"""Optional waveform, differential-plane, and alarm visualization."""

import matplotlib.pyplot as plt
import numpy as np


def plot_snapshot(time_s, current_a, idiff_pu, irest_pu, alarms=()):
    values = np.asarray(current_a)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError("current_a must contain three phase columns")
    figure, (wave_axis, plane_axis) = plt.subplots(1, 2, figsize=(12, 4))
    wave_axis.plot(time_s, values)
    wave_axis.set(title="Simulated three-phase current", xlabel="Time (s)", ylabel="A")
    plane_axis.scatter(irest_pu, idiff_pu, c="red" if alarms else "green")
    plane_axis.set(title="87T differential operating point", xlabel="Irestraint (pu)", ylabel="Idifferential (pu)")
    if alarms:
        figure.suptitle("IDS ALARM: " + ", ".join(alarms), color="red")
    figure.tight_layout()
    return figure
