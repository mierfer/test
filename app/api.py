"""REST API blueprint for extensibility — headless CMS, third-party integrations."""
from flask import Blueprint, jsonify, request, abort
from app.models import Post, Category, Tag

api = Blueprint("api", __name__)


def _post_to_dict(p):
    return {
        "id": p.id,
        "title": p.title,
        "slug": p.slug,
        "summary": p.summary,
        "content": p.content,
        "cover_image": p.cover_image,
        "category": p.category.name if p.category else None,
        "tags": [t.name for t in p.tags],
        "author": p.author.username,
        "views": p.views,
        "is_featured": p.is_featured,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


@api.route("/posts")
def get_posts():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    category = request.args.get("category")

    query = Post.query.filter_by(is_published=True)
    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "posts": [_post_to_dict(p) for p in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page,
        }
    )


@api.route("/posts/<slug>")
def get_post(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first()
    if not post:
        abort(404)
    return jsonify(_post_to_dict(post))


@api.route("/categories")
def get_categories():
    cats = Category.query.all()
    return jsonify(
        [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "description": c.description,
                "post_count": c.posts.filter_by(is_published=True).count(),
            }
            for c in cats
        ]
    )


@api.route("/tags")
def get_tags():
    tags = Tag.query.all()
    return jsonify(
        [
            {"id": t.id, "name": t.name, "slug": t.slug, "post_count": t.posts.count()}
            for t in tags
        ]
    )
