# Field Note 01 — The Math That Lets a Tower Catch a Rocket

A falling rocket can't just aim at the ground. It has a fixed fuel budget, an engine that can't throttle down to zero, and it has to arrive at one exact point with zero velocity. `lander.py` solves that problem in about fifty lines of Python: it finds the fuel-optimal thrust profile for a simplified lander, as a single convex optimization problem.

**What this is not:** SpaceX hasn't published Starship's guidance code. This is a teaching model of the published family of math behind powered-descent guidance (convex optimization with *lossless convexification*), not a reconstruction of any company's flight software.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python lander.py
```

It tries every whole-second time of flight from 20 to 60 s and keeps the one that burns the least fuel. The full search takes about 20–30 s on a laptop. You should see:

```
20 s: infeasible
21 s: fuel 252.1 kg
22 s: fuel 235.0 kg
23 s: fuel 236.7 kg
time of flight 22 s, fuel used 235.0 kg
max |T - Gamma| = 0.062 N (at the 61 sample points)
thrust range 12000 .. 31988 N (limits 12000 .. 32000)
```

It also saves the trajectory to `solution.npz` (time, position, velocity, thrust, slack, mass) for plotting.

## How to read the output

- **20 s: infeasible.** With these throttle limits there's no legal way to stop in 20 seconds. The solver proves it rather than crashing into the ground.
- **22 s wins.** Of the whole-second times tried, 22 s uses the least fuel. Shorter landings need harder braking; longer ones waste fuel fighting gravity.
- **max |T − Γ| ≈ 0.** The trick in this problem is replacing the hard, non-convex constraint "thrust must stay between 30% and 80%" with a convex relaxation using a slack variable Γ. If the relaxation is exact ("lossless"), the real thrust T equals Γ. At every sample point checked, it matches to within a tenth of a newton. (Only the 61 sample points are checked, not the instants between them.)
- **Thrust sits on its limits.** The fuel-optimal profile is "bang-bang": minimum throttle, then maximum. Watch the throttle in the video.

## The model

| Parameter | Value |
|---|---|
| Wet / dry mass | 2000 kg / 1500 kg |
| Specific impulse | 250 s |
| Max thrust | 40 kN, throttle window 30–80% (12–32 kN) |
| Start position (x, y, altitude) | (600, 200, 1500) m |
| Start velocity | (−30, 10, −75) m/s |
| Glide-slope cone | at least 30° above the ground |
| Time steps | 60 (thrust linear between samples) |

Simplifications: a point mass in 3D (no attitude dynamics), flat ground, constant gravity, no atmosphere or wind, a single engine.

Change any of these at the top of `lander.py` and rerun to see how the landing changes.

## References

- B. Açıkmeşe and S. R. Ploen, "Convex Programming Approach to Powered Descent Guidance for Mars Landing," *Journal of Guidance, Control, and Dynamics*, 30(5), 2007.
- L. Blackmore, B. Açıkmeşe and D. P. Scharf, "Minimum-Landing-Error Powered-Descent Guidance for Mars Landing Using Convex Optimization," *Journal of Guidance, Control, and Dynamics*, 33(4), 2010.
- D. Malyuta et al., "Advances in Trajectory Optimization for Space Vehicle Control," [arXiv:2108.02335](https://arxiv.org/abs/2108.02335), 2021. A readable survey, including G-FOLD's flight tests.
