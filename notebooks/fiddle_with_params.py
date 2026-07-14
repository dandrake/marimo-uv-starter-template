import marimo

__generated_with = "0.13.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import math

    return math, mo


@app.cell
def _(math):
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


    return archimedean_spiral_bezier, epitrochoid_bezier


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # Basic interactivity example for fiddling with curve parameters

    This is just a little demo, showing basic Marimo UI elements --
    sliders, positioning, and embedding HTML to show the SVG we build as
    part of the logo.
    """
    )
    return


@app.cell
def _(math, mo):
    # it seems like you should be able to do `phase = ...` here, and use
    # that below -- that works when not using the array and vstack and
    # so on.
    _phase = mo.ui.slider(start=-math.pi, stop=math.pi, step=0.05, value=0, show_value=True, label="Spiral phase:")
    _display_size = mo.ui.slider(start=0.1, stop=1.5, step=0.02, value=1, show_value=True, label="Display size:")
    _turns = mo.ui.slider(start=1.75, stop=3, step=.05, value=2.15, show_value=True, label="Number of spiral turns:")
    _fit = mo.ui.slider(start=12, stop=22, step=.25, value=16, show_value=True, label="Spiral tightness:")


    sliders_left = mo.ui.array([_phase, _display_size])
    sliders_right = mo.ui.array([_turns, _fit])

    mo.hstack([mo.vstack(sliders_left),
               mo.vstack(sliders_right)],
              )
    return sliders_left, sliders_right


@app.cell(hide_code=True)
def _(
    archimedean_spiral_bezier,
    epitrochoid_bezier,
    mo,
    sliders_left,
    sliders_right,
):
    phase = sliders_left.value[0]
    display_size = sliders_left.value[1]
    turns = sliders_right.value[0]
    fit = sliders_right.value[1]

    petals = epitrochoid_bezier(petals=5, loop_depth=2.0, segments=40)
    spiral = archimedean_spiral_bezier(turns=turns, segments=20, fit=fit, phase=phase)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
         <path d="{petals}" fill="none" stroke="#DE3A28" stroke-width="3.2"
                stroke-linejoin="round" stroke-linecap="round"/>
          <path d="{spiral}" fill="none" stroke="#DE3A28" stroke-width="3"
                stroke-linecap="round"/>
        </svg>'''

    html = f'<div style="transform: scale({display_size}); transform-origin: top left;">' + svg + '</div>'

    mo.Html(f"<span> </span>" + html)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
