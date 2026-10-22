# 5. Preamp study: would a preamp stage improve this amp?

Question asked 2026-10-22 for the real goal: a quiet, customizable 1 W desk / nightstand amplifier fed
from a phone, PC or DAC. Decks: `sim/amp_noise2.cir` (the channel as built), `sim/preamp.cir` and
`sim/preamp_noise.cir` (two candidate stages). ngspice 42, generic models.

## 5.1 What the amp already does with a line-level source

| Pot position (source resistance seen by the amp) | Gain | Input for 1 W into 8 ohm | Output noise 20 Hz-20 kHz | SNR at 1 W | SNR at 50 mW (desk level) |
|---|---|---|---|---|---|
| fully up (1 ohm) | 20.9 | 135 mVrms | 12.7 uVrms | 107 dB | 94 dB |
| middle of a 10k pot (2.5k) | 19.8 | 143 mVrms | 22.9 uVrms | 102 dB | 89 dB |
| middle of a 50k pot (12.5k) | 16.2 | 175 mVrms | 43.3 uVrms | 96 dB | 83 dB |

A phone gives 0.3 to 1 Vrms, a PC or DAC line output 0.3 to 2 Vrms. The amp reaches full power with
0.14 Vrms, so every normal source already drives it fully; extra gain would only move the clipping
point lower on the knob. Noise at the listening level is 89 to 94 dB below the signal: inaudible at
arm's length. The noise rises with the pot's source resistance, so a 10k pot is the right value
(a 50k pot costs 6 dB).

## 5.2 Candidate preamp stages (sim/preamp.cir)

| Stage | Gain | Zin | Input noise (20 Hz-20 kHz) | THD at 0.5 Vpk out | What it is for |
|---|---|---|---|---|---|
| A: bootstrapped BC547 emitter follower | 0.88 | 835k | 0.11 uV (low-Z source), 0.97 uV (2.5k), 13.6 uV (100k guitar pickup) | 0.09% (0.2% at 1 Vpk) | high-impedance sources, long cable to the pot |
| B: BC547 gain stage, +15 dB | 6.0 | 22k | 1.08 uV (2k source) | 0.11% | low-level sources (dynamic mic, passive guitar) |

Both add distortion of the same order as the power amp's own 0.03 to 0.2 percent and add a little noise;
neither improves anything for a phone, PC or DAC.

## 5.3 Verdict

- **For the stated use (line-level source, 1 W, desk): no preamp.** It would add parts and 0.1 to 0.2
  percent THD and buy nothing. The amp's sensitivity, noise and input impedance are already right.
- **A buffer earns its place only in front of the volume pot** if you want a 1 M-ohm input (passive
  guitar, old radios, a long input cable) or to stop the 10 percent gain change across the knob.
- **A preamp becomes worthwhile when it carries features**, not gain: a Baxandall bass/treble or a
  loudness contour for small nightstand speakers (needs about 20 dB of make-up gain, which is what a
  preamp stage is for), an input selector, or a mix of two sources. That is a fourth board between the
  volume board and the amp, with a bypass jumper, not a change to the amp.

## 5.4 What would move this amp towards "audiophile" instead (release 2 candidates, unsimulated)

1. Output stage distortion: 0.03 percent (8 ohm) to 0.18 percent (4 ohm) at 50 mW is the crossover
   region of a single BD139/BD140 pair. A current-mirror load on the differential pair plus a
   constant-current tail, or Darlington / CFP outputs, should bring it under 0.01 percent.
2. Output capacitor: 1000 uF gives -3 dB at 34 Hz into 4 ohm; 2200 uF halves that. Removing it needs a
   split supply, which is a different PSU.
3. Supply: the zener follower's 0.4 V load regulation is fine, but a capacitance multiplier or a
   feedback regulator would lower ripple further for near-field listening.
4. Headphone output for the nightstand: the 1 W output drives 32 ohm headphones through 100 to 220 ohm
   series resistors and a switched jack; no preamp needed.
5. Lower-noise input pair (BC550C) and a 5k log pot: about 3 dB.
