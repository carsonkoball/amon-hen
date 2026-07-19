from flask import Flask, render_template

import config
from routes.scripts import scripts_bp

amon_hen_ui = Flask(__name__)

amon_hen_ui.register_blueprint(scripts_bp)


@amon_hen_ui.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        title="Dashboard",
        description="A collection of tools for monitoring data sources to support investment research.",
        back_link_visibility="hidden",
        scripts=config.SCRIPTS,
    )


if __name__ == "__main__":
    amon_hen_ui.run(debug=True)
