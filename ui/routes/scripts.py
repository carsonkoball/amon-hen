from flask import Blueprint, abort

import config
from handlers import HANDLERS

scripts_bp = Blueprint("scripts", __name__)


@scripts_bp.route("/<slug>", methods=["GET", "POST"])
def script_page(slug):

    script = next((s for s in config.SCRIPTS if s["slug"] == slug), None)

    if script is None:
        abort(404)

    handler = HANDLERS.get(slug)

    if handler is None:
        abort(404)

    return handler.handle(script)
