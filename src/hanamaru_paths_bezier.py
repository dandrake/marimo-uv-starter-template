"""
hanamaru_paths_bezier.py
------------------------
Same two marks as hanamaru_paths.py, but emitted as smooth cubic-Bezier
paths instead of dense polylines.

The trick: these curves are analytic, so at every knot we know the exact
tangent (the derivative), not just the position.  A cubic Bezier segment is
fully determined by its two endpoints and the tangents there (a Hermite
segment), so we convert Hermite -> Bezier directly:

    for a segment from P_i to P_{i+1} spanning a parameter step h,
    with exact velocities m_i, m_{i+1} = dP/dt at the knots:

        B0 = P_i
        B1 = P_i     + (h/3) * m_i
        B2 = P_{i+1} - (h/3) * m_{i+1}
        B3 = P_{i+1}

Because the tangents are exact (not finite-difference guesses like
Catmull-Rom), a handful of segments matches the true curve to a small
fraction of a pixel:

        petals  : 40 segments -> max error 0.020 px  (was 340 chords)
        spiral  : 20 segments -> max error 0.020 px  (was 360 chords)

Placement (rotate about origin, uniform scale, translate to centre) is
linear, so it applies to the velocity too -- minus the translation, which
differentiates away.
"""

from __future__ import annotations
import math


# ---- placement: same affine map applied to points and (sans shift) tangents
def _place_point(p, *, scale, rot, center):
    (x, y), (cx, cy) = p, center
    c, s = math.cos(rot), math.sin(rot)
    return (cx + (x * c - y * s) * scale, cy + (x * s + y * c) * scale)

def _place_vec(v, *, scale, rot):            # derivative: no translation term
    x, y = v
    c, s = math.cos(rot), math.sin(rot)
    return ((x * c - y * s) * scale, (x * s + y * c) * scale)


def _hermite_to_path(knots, P, M, h, *, decimals, closed):
    """Emit an SVG path from placed points P, placed velocities M, step h."""
    f = lambda x, y: f"{x:.{decimals}f},{y:.{decimals}f}"
    d = "M" + f(*P[0])
    n = len(knots)
    last = n if closed else n - 1
    for i in range(last):
        j = (i + 1) % n
        b1 = (P[i][0] + h / 3 * M[i][0], P[i][1] + h / 3 * M[i][1])
        b2 = (P[j][0] - h / 3 * M[j][0], P[j][1] - h / 3 * M[j][1])
        d += "C" + f(*b1) + " " + f(*b2) + " " + f(*P[j])
    return d + ("Z" if closed else "")


# --------------------------------------------------------------------------
# petals: prolate epitrochoid  x=k cos t - d cos(kt),  y=k sin t - d sin(kt)
# --------------------------------------------------------------------------
def epitrochoid_bezier(petals: int = 5, loop_depth: float = 2.0, *,
                       segments: int = 40, fit: float = 40.0,
                       center=(50.0, 50.0), rot: float = -math.pi / 2,
                       decimals: int = 2) -> str:
    k, d = petals + 1, loop_depth
    scale = fit / (k + d)                     # k+d is the tip radius
    h = 2 * math.pi / segments
    knots = [i * h for i in range(segments)]  # closed: no duplicate endpoint

    def pos(t): return (k*math.cos(t) - d*math.cos(k*t),
                        k*math.sin(t) - d*math.sin(k*t))
    def vel(t): return (-k*math.sin(t) + d*k*math.sin(k*t),
                         k*math.cos(t) - d*k*math.cos(k*t))

    P = [_place_point(pos(t), scale=scale, rot=rot, center=center) for t in knots]
    M = [_place_vec(vel(t), scale=scale, rot=rot) for t in knots]
    return _hermite_to_path(knots, P, M, h, decimals=decimals, closed=True)


# --------------------------------------------------------------------------
# centre: Archimedean spiral  r = a*theta  ->  (a t cos t, a t sin t)
# --------------------------------------------------------------------------
def archimedean_spiral_bezier(turns: float = 2.75, *, segments: int = 20,
                              fit: float = 14.0, center=(50.0, 50.0),
                              decimals: int = 2, phase: float = 0.0) -> str:
    cx, cy = center
    t_max = turns * 2 * math.pi
    a = fit / t_max
    h = t_max / segments
    knots = [i * h for i in range(segments + 1)]  # open: keep both endpoints

    def pos(t, p): return (a*t*math.cos(t + p), a*t*math.sin(t + p))
    def vel(t, p): return (a*(math.cos(t + p) - t*math.sin(t+p)),
                        a*(math.sin(t+p) + (t+p)*math.cos(t+p)))

    P = [(cx + pos(t, phase)[0], cy + pos(t, phase)[1]) for t in knots]
    M = [vel(t, phase) for t in knots]
    return _hermite_to_path(knots, P, M, h, decimals=decimals, closed=False)


if __name__ == "__main__":
    petals = epitrochoid_bezier(petals=5, loop_depth=2.0, segments=40)

    # phase = 0 hits the petal 3rd from the top one; move it halfway to
    # the previous petal -- 1/10 of the way around
    phase = -(2 * math.pi) / 10
    spiral = archimedean_spiral_bezier(turns=2.15, segments=20, fit=16, phase=phase)

    print(f"petals: {petals.count('C')} cubic segments, {len(petals)} chars")
    print(f'  d="{petals}"\n')
    print(f"spiral: {spiral.count('C')} cubic segments, {len(spiral)} chars")
    print(f'  d="{spiral}"\n')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="{petals}" fill="none" stroke="#DE3A28" stroke-width="3.2"
        stroke-linejoin="round" stroke-linecap="round"/>
  <path d="{spiral}" fill="none" stroke="#DE3A28" stroke-width="3"
        stroke-linecap="round"/>
</svg>'''
    with open("hanamaru_primary_bezier.svg", "w") as fh:
        fh.write(svg)
    print("wrote hanamaru_primary_bezier.svg")
