import marimo

__generated_with = "0.13.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import hanamaru_paths_bezier as logo
    import math

    return logo, math, mo


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
def _(logo, mo, sliders_left, sliders_right):
    phase = sliders_left.value[0]
    display_size = sliders_left.value[1]
    turns = sliders_right.value[0]
    fit = sliders_right.value[1]

    petals = logo.epitrochoid_bezier(petals=5, loop_depth=2.0, segments=40)
    spiral = logo.archimedean_spiral_bezier(turns=turns, segments=20, fit=fit, phase=phase)
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
