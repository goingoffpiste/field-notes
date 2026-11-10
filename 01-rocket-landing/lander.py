"""Field Note 01 - The math that lets a tower catch a rocket.

Fuel-optimal powered-descent guidance as one convex program (lossless convexification).
Formulation follows Acikmese & Ploen (2007) and Blackmore, Acikmese & Scharf (2010):
3-DoF point-mass lander, thrust bounded above AND below (engine can't go to zero),
glide-slope cone, change of variables u = T/m, sigma = Gamma/m, z = ln m.
"""
import numpy as np
import cvxpy as cp

g = np.array([0.0, 0.0, -9.81])           # gravity, m/s^2
m_wet, m_dry = 2000.0, 1500.0              # kg
Isp = 250.0                                # s
alpha = 1.0 / (Isp * 9.81)                 # kg of fuel per N*s of thrust
T_max = 40_000.0                           # N
rho1, rho2 = 0.3 * T_max, 0.8 * T_max      # throttle window: 30% .. 80%
glide = np.radians(30)                     # min glide-slope angle above ground
r0, v0 = np.array([600.0, 200.0, 1500.0]), np.array([-30.0, 10.0, -75.0])


def solve(tf, N=60):
    dt = tf / N
    r, v = cp.Variable((3, N + 1)), cp.Variable((3, N + 1))
    u, sig, z = cp.Variable((3, N + 1)), cp.Variable(N + 1), cp.Variable(N + 1)
    t = np.arange(N + 1) * dt
    z0 = np.log(m_wet - alpha * rho2 * t)          # reference log-mass (heaviest-burn bound)
    cons = [r[:, 0] == r0, v[:, 0] == v0, z[0] == np.log(m_wet),
            r[:, N] == 0, v[:, N] == 0, z[N] >= np.log(m_dry)]
    for k in range(N):
        cons += [v[:, k + 1] == v[:, k] + dt / 2 * (u[:, k] + u[:, k + 1]) + dt * g,
                 r[:, k + 1] == r[:, k] + dt / 2 * (v[:, k] + v[:, k + 1])
                 - dt**2 / 12 * (u[:, k + 1] - u[:, k]),
                 z[k + 1] == z[k] - alpha * dt / 2 * (sig[k] + sig[k + 1])]
    for k in range(N + 1):
        dz = z[k] - z0[k]
        mu1, mu2 = rho1 * np.exp(-z0[k]), rho2 * np.exp(-z0[k])
        cons += [cp.norm(u[:, k]) <= sig[k],                          # the relaxation
                 mu1 * (1 - dz + cp.square(dz) / 2) <= sig[k],        # lower thrust bound
                 sig[k] <= mu2 * (1 - dz),                            # upper thrust bound
                 cp.norm(r[:2, k]) * np.tan(glide) <= r[2, k]]        # glide-slope cone
    prob = cp.Problem(cp.Maximize(z[N]), cons)                        # keep the most mass
    prob.solve(solver=cp.CLARABEL)
    return prob, r, v, u, sig, z, t


if __name__ == "__main__":
    best = None
    for tf in np.arange(20, 61, 1.0):                                 # search time of flight
        prob, *rest = solve(tf)
        ok = prob.status == "optimal"
        if tf <= 23:
            print(f"{tf:.0f} s: " + (f"fuel {m_wet - np.exp(prob.value):.1f} kg" if ok else "infeasible"))
        if ok and (best is None or prob.value > best[0].value):
            best = (prob, tf, *rest)
    prob, tf, r, v, u, sig, z, t = best
    m = np.exp(z.value)
    T = np.linalg.norm(u.value, axis=0) * m                           # actual thrust, N
    G = sig.value * m                                                 # slack Gamma, N
    print(f"time of flight {tf:.0f} s, fuel used {m_wet - m[-1]:.1f} kg")
    print(f"max |T - Gamma| = {np.max(np.abs(T - G)):.3f} N (at the {len(t)} sample points)")
    print(f"thrust range {T.min():.0f} .. {T.max():.0f} N (limits {rho1:.0f} .. {rho2:.0f})")
    np.savez("solution.npz", t=t, r=r.value, v=v.value, T=T, G=G, m=m, tf=tf)
