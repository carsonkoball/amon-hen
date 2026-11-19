from flask import render_template, request

from amon_hen.tools import adp_tracker


def application_count_change(result):
    """
    Check if difference is caused ONLY by application count update.
    """
    if len(result.differences) == 1:
        if result.differences[0].path == ("data", "customFieldGroup", "numberFields"):
            if isinstance(result.differences[0].old, list):
                if isinstance(result.differences[0].old[0], dict):
                    if (
                        result.differences[0].old[0]["categoryCode"]["codeValue"]
                        == "ApplicantCount"
                    ):
                        if (
                            result.differences[0].old[0]["numberValue"]
                            != result.differences[0].new[0]["numberValue"]
                        ):
                            return True

    return False


def handle(script):
    cid = ""
    ccid = ""
    results = None

    if request.method == "POST":
        cid = request.form["cid"]
        ccid = request.form["ccid"]

        results = adp_tracker.run(cid=cid, ccid=ccid)
        results = [result for result in results if not application_count_change(result)]

    return render_template(
        "adp_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        cid=cid,
        ccid=ccid,
        results=results,
    )
