from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.security import login_rate_limit, rate_limit

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
@login_rate_limit
def login():
    if current_user.is_authenticated:
        return redirect(url_for("blog.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"欢迎回来，{user.username}！", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("blog.index"))
        flash("用户名或密码错误", "error")

    return render_template("auth/login.html")


@auth.route("/register", methods=["GET", "POST"])
@rate_limit(max_requests=3, window_seconds=3600)
def register():
    if current_user.is_authenticated:
        return redirect(url_for("blog.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not email or not password:
            flash("请填写所有字段", "error")
        elif len(username) < 2 or len(username) > 64:
            flash("用户名长度需在2-64字符之间", "error")
        elif password != confirm:
            flash("两次密码输入不一致", "error")
        elif len(password) < 6:
            flash("密码长度至少6位", "error")
        elif User.query.filter_by(username=username).first():
            flash("该用户名已被注册", "error")
        elif User.query.filter_by(email=email).first():
            flash("该邮箱已被注册", "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("注册成功，请登录", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("blog.index"))
