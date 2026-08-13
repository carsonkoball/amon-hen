from datetime import date

from flask import render_template, request

from amon_hen.tools import fcc_els_parser


def handle(script):
    results = None
    search_date = date.today()

    if request.method == "POST":
        search_date = date.fromisoformat(request.form["search_date"])

        results = fcc_els_parser.run(search_date=search_date)

    return render_template(
        "fcc_els_parser.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        search_date=search_date,
        results=results,
    )
