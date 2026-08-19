from datetime import date

from flask import render_template, request

from amon_hen.tools import navy_sbir_parser


def handle(script):
    results = None
    start_date = date.today()
    end_date = date.today()
    
    if request.method == "POST":
        start_date = date.fromisoformat(request.form["start_date"])
        end_state = date.fromisoformat(request.form["end_date"])

        results = navy_sbir_parser.run(start_date=start_date, end_date=end_date)

    return render_template(
        "navy_sbir_parser.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
		start_date=start_date,
		end_date=end_date,
        results=results,
    )
