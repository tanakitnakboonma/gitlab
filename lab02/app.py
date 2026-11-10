from flask import Flask, render_template, request

from dc_bias import calculate_dc_bias, kohm_to_ohm

app = Flask(__name__)

DEFAULTS = {
    "vcc": "12", "r1": "100", "r2": "22", "rc": "2.2",
    "re": "1", "beta": "100", "vbe": "0.70",
}


@app.get("/")
def index():
    return render_template("index.html", form=DEFAULTS, result=None, error=None)


@app.post("/calculate")
def calculate():
    form = {key: request.form.get(key, "") for key in DEFAULTS}
    try:
        result = calculate_dc_bias(
            vcc=form["vcc"],
            r1=kohm_to_ohm(form["r1"]),
            r2=kohm_to_ohm(form["r2"]),
            rc=kohm_to_ohm(form["rc"]),
            re=kohm_to_ohm(form["re"]),
            beta=form["beta"],
            vbe=form["vbe"],
        )
    except ValueError as error:
        return render_template("index.html", form=form, result=None, error=str(error))

    return render_template("index.html", form=form, result=result, error=None)
