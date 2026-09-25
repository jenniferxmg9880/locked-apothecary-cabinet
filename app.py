"""
The Locked Apothecary Cabinet
------------------------------
A deliberately vulnerable Flask app built for a CTF exercise.

THE VULNERABILITY (for the challenge author's reference — this
docstring is server-side only, players never see it):

`sanitize_filename()` below defends against path traversal by
stripping the literal substring "../" from user input. That is a
single, non-recursive pass: Python's str.replace() scans the string
once, left to right, and does not re-scan its own output. So input
like "....//" is NOT caught — removing the one "../" match found
inside "....//" leaves behind "../" itself:

    "....//".replace("../", "")  ->  "../"

This is a well-known, widely-taught blacklist bypass (PortSwigger's
Web Security Academy uses the same technique). The intended solve:

    GET /recipe?name=....//restricted/forbidden_formulae.txt

Absolute paths (leading "/", drive letters, backslashes) are blocked
outright, so the *intended* lesson is the blacklist-bypass technique
specifically, not just "the filter is missing entirely."
"""

from flask import Flask, request, render_template, abort
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPES_DIR = os.path.join(BASE_DIR, "recipes")

RECIPES = [
    {"file": "wolfsbane_tincture.txt", "label": "Wolfsbane Tincture"},
    {"file": "nightshade_extract.txt", "label": "Nightshade Extract"},
    {"file": "oleander_draught.txt", "label": "Oleander Draught"},
    {"file": "hemlock_reduction.txt", "label": "Hemlock Reduction"},
    {"file": "deathstalker_venom.txt", "label": "Deathstalker Venom, Decanted"},
    {"file": "blister_beetle_powder.txt", "label": "Blister Beetle Powder"},
]


def sanitize_filename(name):
    """Intentionally weak: a single, non-recursive blacklist pass."""
    cleaned = name.replace("../", "")
    if cleaned.startswith("/") or cleaned.startswith("\\") or ":" in cleaned:
        abort(403)
    return cleaned


@app.route("/")
def index():
    return render_template("index.html", recipes=RECIPES)


@app.route("/recipe")
def recipe():
    name = request.args.get("name", "")
    if not name:
        abort(400)

    safe_name = sanitize_filename(name)
    path = os.path.join(RECIPES_DIR, safe_name)

    if not os.path.isfile(path):
        abort(404)

    with open(path, "r", errors="replace") as f:
        content = f.read()

    return render_template("recipe.html", requested=name, content=content)


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="That page doesn't exist in this archive."), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, message="That path is blocked outright."), 403


@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", code=400, message="No recipe name was given."), 400


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
