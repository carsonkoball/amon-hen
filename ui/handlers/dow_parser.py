from datetime import date

from flask import render_template, request

from amon_hen.tools import dow_parser


def handle(script):
    results = None
    start_date = date.today()
    end_date = date.today()

    if request.method == "POST":
        start_date = date.fromisoformat(request.form["start_date"])
        end_date = date.fromisoformat(request.form["end_date"])

        results = dow_parser.run(start_date=start_date, end_date=end_date)

    # Group by date for easier display
    if results:
        parsed_results = {}

        for result in results:
            parsed_results.setdefault(result.date, []).append(result)

        results = parsed_results

    return render_template(
        "dow_parser.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        start_date=start_date,
        end_date=end_date,
        results=results,
    )
