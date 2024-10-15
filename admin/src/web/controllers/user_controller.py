from flask import render_template, url_for, redirect
from flask import Blueprint
from src.model.auth.operations import user_operations
from src.model.auth.operations import role_operations
from src.web.handlers.check_permissions import permission_required
from src.model.auth.tables.user import User
from .auth import password_is_valid, domain_exists, is_valid_email
from flask import session
from flask import abort
from flask import flash
from flask import request
from src.web.handlers.check_permissions import login_required


bp = Blueprint("user", __name__, url_prefix="/usuarios")

@bp.get("/eliminar/<id>")
@permission_required('user_destroy')
def delete(id):
    real_id = 0
    try:
        real_id = int(id)
        user_operations.delete_user(real_id)
    except:
        flash("Uso inválido de parametros, no se pudo eliminar al usuario", "error")
    return redirect(url_for("user.index"))

@bp.get("/perfil/<alias>")
@permission_required('user_show')
def view_user(alias):
    user = user_operations.get_user_by_alias(alias)
    if user:
        roles = role_operations.list_roles()
        roles = [role.name for role in roles]
        users = user_operations.list_users()
        mails = [user.email for user in users]
        aliases = [user.alias for user in users]
        mails.remove(user.email)
        aliases.remove(alias)
        return render_template("auth/view_user.html", user=user, roles=roles, mails=mails, aliases=aliases)
    else:
        return abort(404)
    
@bp.get('/miperfil')
@login_required()
def myprofile():
    user = user_operations.get_user_by_email(session.get("user"))
    roles = role_operations.list_roles()
    roles = [role.name for role in roles]
    users = user_operations.list_users()
    mails = [user.email for user in users]
    aliases = [user.alias for user in users]
    mails.remove(user.email)
    aliases.remove(user.alias)
    return render_template("auth/view_user.html", user=user, roles=roles, mails=mails, aliases=aliases)

@bp.post("/update/<id>")
@permission_required('user_update')
def update(id):
    params = request.form
    mail = str(params.get("email"))
    alias = str(params.get("alias"))
    password = str(params.get("password"))
    checkMail = user_operations.get_user_by_email(mail)
    checkAlias = user_operations.get_user_by_alias(alias)
    enabled = params.get("enabled") is None
    role = str(params.get("role"))

    try:
        real_id = int(id)
        user = user_operations.get_user(real_id)
        if ((mail != "None" and mail != "") or (alias != "None" and alias != "") or (password != "None" and password != "")) and user.email != session.get("user"):
            flash("No se puede modificar información privada de los usuarios", "error")
            return redirect((url_for("user.view_user", alias=user.alias)))
        if not (not checkMail or (checkMail.id == real_id)) and (not checkAlias or (checkAlias.id == real_id)):
            flash("Lo lamentamos, ha habido un error inesperado", "error")
            return redirect((url_for("user.view_user", alias=user.alias)))
        if (password != "None" and password != "" and not password_is_valid(password)):
            flash("La contraseña no cumple con los patrones solicitados", "error")
            return redirect((url_for("user.view_user", alias=user.alias)))
        if (mail != "None" and mail != "") and ((not is_valid_email(mail)) or (not domain_exists(mail))):
            flash("La dirección de mail ingresada no es válida", "error")
            return redirect((url_for("user.view_user", alias=user.alias)))
        if params["role"] == "Administrador de Sistema":
            enabled = True
        role = role_operations.search_name(role)
        role_id = None
        if role:
            role_id = role.id
        if mail == "None" or mail == "":
            mail = user.email
        if password == "None" or password == "":
            password = None
        if alias == "None" or alias == "":
            alias = user.alias
        user = User(mail, alias, password, enabled=enabled, role_id=role_id)
        user.id = real_id
        user_operations.update_user(user)
        if mail != "None" and mail == "":
            del session["user"]
            session.clear()
            session["user"] = user.email
        return redirect(url_for("user.view_user", alias=user.alias))
    except:
        flash("Uso inválido de parametros, no se pudo actualizar al usuario", "error")
        return redirect(url_for("home"))

@bp.get("/")
@permission_required('user_index')
def index():
    roles = role_operations.list_roles()
    roles = [role.name for role in roles]

    mail = request.args.get('mail')
    page = request.args.get('page')
    role = request.args.get('role')
    ascending = request.args.get('ascending') is None
    users = user_operations.start_query()
    retMail=""
    retRole=""
    orderMail = request.args.get('order_email') is not None
    try:
        if not page:
            page = 1
        else:
            page = int(page)
        if mail:
            users = user_operations.search_by_mail(users, str(mail))
            retMail=mail
        if role:
            users = user_operations.filter_role(users, str(role))
            retRole=role
        if not orderMail:
            users = user_operations.sorted_by_attribute(users=users, attribute="email", ascending=ascending)
        else:
            users = user_operations.sorted_by_attribute(users, "inserted_at", ascending)
        if request.args.get('status'):
            users = user_operations.filter_active(users, bool(int(request.args.get('value'))))
    except:
        flash("Uso inválido de parametros, no se pudo aplicar el filtro", "error")
        page = 0
    finally:
        data = user_operations.get_paginated_list(users, page)

        users = data[0]
        pages = data[1]
        return render_template("user_search.html", pages=pages, users=users, roles=roles, status=request.args.get('status'), startMail=retMail, startRole=retRole, startAscending=(not ascending), enabled=request.args.get('value'), orderMail=orderMail, startPage=page)