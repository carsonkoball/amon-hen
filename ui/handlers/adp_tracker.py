from flask import render_template, request

from amon_hen.scripts import adp_tracker


def handle(script):
    new_jobs = None
    removed_jobs = None

    if request.method == "POST":
        cid = request.form["cid"]
        ccid = request.form["ccid"]

        results = adp_tracker.run(cid=cid, ccid=ccid)

        new_jobs = results["new_jobs"]
        removed_jobs = results["removed_jobs"]

    return render_template(
        "adp_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        new_jobs=new_jobs,
        removed_jobs=removed_jobs,
    )
