from hashlib import sha256
import json

from flask import render_template, request

from amon_hen.tools import diu_pathway_tracker


def handle(script):
    cso_results, ccao_results = None, None

    if request.method == "POST":
        cso_results, ccao_results = diu_pathway_tracker.run()

    return render_template(
        "diu_pathway_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        cso_results=cso_results,
        ccao_results=ccao_results,
    )
