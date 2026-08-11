from flask import render_template, request

from amon_hen.tools import adp_tracker


def handle(script):
    cid = ""
    ccid = ""
    results = None

    if request.method == "POST":
        cid = request.form["cid"]
        ccid = request.form["ccid"]

        results = adp_tracker.run(cid=cid, ccid=ccid)

    return render_template(
        "adp_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        cid=cid,
        ccid=ccid,
        results=results,
    )
