from hashlib import sha256
import json

from flask import render_template, request

from amon_hen.tools import blue_list_tracker


def handle(script):
    cleared_results = None
    framework_results = None

    if request.method == "POST":
        cleared_results, framework_results = blue_list_tracker.run()
    if cleared_results:
        print(json.dumps(cleared_results[0].new_data, indent=2))
    return render_template(
        "blue_list_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        cleared_results=cleared_results,
        framework_results=framework_results,
    )
