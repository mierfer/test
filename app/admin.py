import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, current_app
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Post, Category, Tag, User, Comment

admin = Blueprint("admin", __name__)


def admin_required(f):
    """Decorator that checks admin permission before route access."""
    from functools import wraps

    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash("需要管理员权限", "error")
            return redirect(url_for("blog.index"))
        return f(*args, **kwargs)

    return decorated


@admin.route("/")
@admin_required
def dashboard():
    stats = {
        "posts": Post.query.count(),
        "published": Post.query.filter_by(is_published=True).count(),
        "drafts": Post.query.filter_by(is_published=False).count(),
        "categories": Category.query.count(),
        "tags": Tag.query.count(),
        "users": User.query.count(),
        "comments": Comment.query.count(),
        "views": db.session.query(db.func.sum(Post.views)).scalar() or 0,
    }
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(10).all()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_posts=recent_posts,
        recent_comments=recent_comments,
    )


@admin.route("/posts")
@admin_required
def posts():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    return render_template("admin/posts.html", posts=posts)


@admin.route("/post/create", methods=["GET", "POST"])
@admin_required
def create_post():
    categories = Category.query.all()
    tags = Tag.query.all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        summary = request.form.get("summary", "").strip()
        content = request.form.get("content", "").strip()
        category_id = request.form.get("category_id", type=int)
        tag_names = request.form.get("tags", "").strip()
        is_published = request.form.get("is_published") == "on"
        is_featured = request.form.get("is_featured") == "on"

        if not title or not content:
            flash("标题和内容不能为空", "error")
            return render_template(
                "admin/edit_post.html", post=None, categories=categories, tags=tags
            )

        post = Post(
            title=title,
            slug=Post.generate_slug(title),
            summary=summary,
            content=content,
            category_id=category_id if category_id else None,
            author_id=current_user.id,
            is_published=is_published,
            is_featured=is_featured,
            cover_image=_handle_upload(request),
        )

        if tag_names:
            for name in tag_names.split(","):
                name = name.strip()
                if name:
                    tag = Tag.query.filter_by(name=name).first()
                    if not tag:
                        slug = Post.generate_slug(name)
                        tag = Tag(name=name, slug=slug)
                        db.session.add(tag)
                    post.tags.append(tag)

        db.session.add(post)
        db.session.commit()
        flash("文章创建成功", "success")
        return redirect(url_for("admin.posts"))

    return render_template(
        "admin/edit_post.html", post=None, categories=categories, tags=tags
    )


@admin.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    categories = Category.query.all()
    tags = Tag.query.all()

    if request.method == "POST":
        post.title = request.form.get("title", "").strip()
        post.summary = request.form.get("summary", "").strip()
        post.content = request.form.get("content", "").strip()
        post.category_id = request.form.get("category_id", type=int)
        post.is_published = request.form.get("is_published") == "on"
        post.is_featured = request.form.get("is_featured") == "on"

        cover = _handle_upload(request)
        if cover:
            post.cover_image = cover

        tag_names = request.form.get("tags", "").strip()
        post.tags = []
        if tag_names:
            for name in tag_names.split(","):
                name = name.strip()
                if name:
                    tag = Tag.query.filter_by(name=name).first()
                    if not tag:
                        slug = Post.generate_slug(name)
                        tag = Tag(name=name, slug=slug)
                        db.session.add(tag)
                    post.tags.append(tag)

        if not post.title or not post.content:
            flash("标题和内容不能为空", "error")
            return render_template(
                "admin/edit_post.html", post=post, categories=categories, tags=tags
            )

        db.session.commit()
        flash("文章更新成功", "success")
        return redirect(url_for("admin.posts"))

    return render_template(
        "admin/edit_post.html", post=post, categories=categories, tags=tags
    )


@admin.route("/post/<int:post_id>/delete", methods=["POST"])
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("文章已删除", "info")
    return redirect(url_for("admin.posts"))


@admin.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if name:
            slug = Post.generate_slug(name)
            cat = Category(name=name, slug=slug, description=description)
            db.session.add(cat)
            db.session.commit()
            flash("分类创建成功", "success")
            return redirect(url_for("admin.categories"))
        flash("分类名称不能为空", "error")

    cats = Category.query.all()
    # Build post count map to avoid lazy-query len() issues in template
    post_counts = {c.id: c.posts.count() for c in cats}
    return render_template("admin/categories.html", categories=cats, post_counts=post_counts)


@admin.route("/category/<int:cat_id>/delete", methods=["POST"])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    Post.query.filter_by(category_id=cat_id).update({"category_id": None})
    db.session.delete(cat)
    db.session.commit()
    flash("分类已删除", "info")
    return redirect(url_for("admin.categories"))


@admin.route("/comments/<int:comment_id>/delete", methods=["POST"])
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("评论已删除", "info")
    return redirect(url_for("admin.dashboard"))


def _handle_upload(req) -> str:
    """Handle image upload, return relative path or empty string."""
    file = req.files.get("cover_image")
    if not file or file.filename == "":
        return ""
    filename = secure_filename(file.filename)
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    return f"/uploads/{filename}"
