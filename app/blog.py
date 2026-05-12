from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from app import db
from app.models import Post, Category, Tag, Comment, User

blog = Blueprint("blog", __name__)


@blog.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    category_slug = request.args.get("category")
    tag_slug = request.args.get("tag")
    search = request.args.get("search", "").strip()

    query = Post.query.filter_by(is_published=True)

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
        query = query.filter(Post.tags.contains(tag))
    if search:
        query = query.filter(Post.title.contains(search) | Post.summary.contains(search))

    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=9, error_out=False
    )

    categories = Category.query.all()
    featured = Post.query.filter_by(is_published=True, is_featured=True).order_by(
        Post.created_at.desc()
    ).limit(4).all()
    recent = Post.query.filter_by(is_published=True).order_by(
        Post.created_at.desc()
    ).limit(5).all()

    return render_template(
        "blog/index.html",
        posts=posts,
        categories=categories,
        featured=featured,
        recent=recent,
        current_category=category_slug,
        current_tag=tag_slug,
        search=search,
    )


@blog.route("/post/<slug>")
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    post.views += 1
    db.session.commit()

    related = (
        Post.query.filter(
            Post.category_id == post.category_id,
            Post.id != post.id,
            Post.is_published == True,  # noqa: E712
        )
        .order_by(Post.created_at.desc())
        .limit(3)
        .all()
    )

    comments = post.comments.order_by(Comment.created_at.desc()).all()

    return render_template("blog/detail.html", post=post, related=related, comments=comments)


@blog.route("/post/<slug>/comment", methods=["POST"])
def add_comment(slug):
    if not current_user.is_authenticated:
        flash("请先登录后再评论", "error")
        return redirect(url_for("auth.login", next=url_for("blog.post_detail", slug=slug)))

    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    content = request.form.get("content", "").strip()

    if not content:
        flash("评论内容不能为空", "error")
    elif len(content) > 2000:
        flash("评论内容不能超过2000字", "error")
    else:
        comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash("评论发表成功", "success")

    return redirect(url_for("blog.post_detail", slug=slug))


@blog.route("/category/<slug>")
def category(slug):
    return redirect(url_for("blog.index", category=slug))


@blog.route("/tag/<slug>")
def tag(slug):
    return redirect(url_for("blog.index", tag=slug))


@blog.route("/search")
def search():
    q = request.args.get("q", "").strip()
    return redirect(url_for("blog.index", search=q))
