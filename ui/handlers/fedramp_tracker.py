from datetime import date

from flask import render_template, request

from amon_hen.tools import fedramp_tracker


def handle(script):
    products_results, agencies_results, assessors_results, advisors_results = (
        None,
        None,
        None,
        None,
    )

    if request.method == "POST":
        products_results, agencies_results, assessors_results, advisors_results = (
            fedramp_tracker.run()
        )

    return render_template(
        "fedramp_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        products_results=products_results,
        agencies_results=agencies_results,
        assessors_results=assessors_results,
        advisors_results=advisors_results,
    )
