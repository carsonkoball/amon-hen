from flask import render_template, request

from amon_hen.scripts import file_tracker


def handle(script):
    results = None

    if request.method == "POST":
        base_url = request.form["base_url"]
        max_depth = request.form["max_depth"]
        max_depth = int(max_depth)
        exhaustive_search = request.form["exhaustive_search"]
        exhaustive_search = True if exhaustive_search == "on" else False
        allowed_extensions = request.form.getlist("allowed_extensions")

        results = file_tracker.run(
            base_url=base_url,
            max_depth=max_depth,
            exhaustive_search=exhaustive_search,
            allowed_extensions=allowed_extensions,
        )

    return render_template(
        "file_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        results=results,
    )
