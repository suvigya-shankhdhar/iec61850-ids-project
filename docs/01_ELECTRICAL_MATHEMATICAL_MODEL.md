# Electrical and mathematical model

## Ratings and sampling

The reference model represents a 60 MVA, 132/33 kV, 50 Hz transformer with YNd11 vector group and 600/1 A and 2400/1 A CTs. The rated line currents are

`I_HV = S/(sqrt(3) V_HV) = 262.43 A` and `I_LV = S/(sqrt(3) V_LV) = 1049.73 A`.

The corresponding CT secondary currents are approximately 0.437 A on both sides. An 80-sample cycle at 50 Hz is sampled at 4000 samples/s. This rate and the configuration reflect an 80-sample/cycle process-bus profile; they are not a claim that every deployment uses the same profile.

## Transient source

`grid_transients.py` creates balanced phase-to-neutral voltages from line-line RMS ratings. The base load current is sinusoidal. A fault adds an RL transient after its inception time. Its decaying DC term uses `tau=L/(Rsource+Rfault)` and its AC magnitude is bounded by the Thevenin impedance. An internal fault is deliberately differential; an external fault is reflected through the ideal 4:1 turns ratio for a restraint demonstration.

The source, transformer, and fault equations form a transparent teaching model, not an electromagnetic-transient program. It omits core hysteresis, mutual coupling, frequency-dependent impedances, CT saturation, breaker arc physics, and detailed zero-sequence networks.

## YNd11 convention and protection

The relay helper accepts three RMS secondary-current phasors in a declared polarity convention. Its YNd11 matrix transforms to symmetrical components, rotates positive sequence by -30 degrees and negative sequence by +30 degrees, and removes zero sequence on the delta side. Thus, a positive-sequence test LV phasor at +30 degrees aligns with the HV reference. Verify phase order, CT polarity, winding connection, zero-sequence filtering, and the direction of compensation before using any other convention or relay.

For compensated current phasors, the model uses:

`Idiff = mean(|IHV + ILV|)` and `Irest = mean((|IHV| + |ILV|)/2)`.

The dual-slope threshold is `pickup + slope1*Irest` up to the breakpoint and adds `slope2*(Irest-breakpoint)` above it. The relay operates only when Idiff exceeds this threshold and the 100 Hz/50 Hz magnitude ratio is below the second-harmonic block setting. The FCDFT uses one full 80-sample window. A practical relay needs manufacturer-specific bias definitions, filtering, saturation detection, and time coordination.

## Inrush

`inrush_model.py` combines a saturated fundamental and a decaying asymmetric component controlled by residual flux. This produces a representative second harmonic for restraint studies, but is not a finite-element/core hysteresis solution. Parameter sweeps should be reported as model sensitivity, not equipment performance.
