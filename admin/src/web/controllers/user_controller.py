from flask import render_template
from flask import Blueprint
from admin.src.model.auth.Operations import user_operations

bp = Blueprint("user", __name__, url_prefix="/usuarios")

@bp.route("/")
def index():
    user = user_operations.list_users()
    return render_template("user/index.html", users = user)
