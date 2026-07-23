from datetime import date

from flask import render_template, request

from amon_hen.scripts import dow_parser


def handle(script):
    results = None

    contract_date = date.today()

    if request.method == "POST":
        contract_date = date.fromisoformat(request.form["contract_date"])

        results = dow_parser.run(contract_date)

    return render_template(
        "dow_parser.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        contract_date=contract_date,
        results=results,
    )
