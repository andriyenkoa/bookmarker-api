from flask_jwt_extended import jwt_required
from flask import Blueprint, request
import validators
from flask.json import jsonify
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from src.database import Bookmark, db
from flasgger import swag_from
from flask_jwt_extended import get_jwt_identity

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route("/", methods=['GET'])
@jwt_required()
@swag_from('./docs/bookmarks/get_bookmarks.yaml')
def get_bookmarks():
    current_user = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    all_bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)

    data = []

    for bookmark in all_bookmarks.items:
        data.append({
            "id": bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at,
        })

    # predefined attributes
    meta = {
        "page": all_bookmarks.page,
        "pages": all_bookmarks.pages,
        "total_count": all_bookmarks.total,
        "prev_page": all_bookmarks.prev_num,
        "next_page": all_bookmarks.next_num,
        "has_next": all_bookmarks.has_next,
        "has_prev": all_bookmarks.has_prev,
    }

    return jsonify({
        "data": data,
        "meta": meta,
    }), HTTP_200_OK


@bookmarks.route("/", methods=['POST'])
@jwt_required()
@swag_from('./docs/bookmarks/post_bookmark.yaml')
def post_bookmark():
    current_user = get_jwt_identity()
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            "error": "Enter a valid URL"
        }), HTTP_400_BAD_REQUEST

    if Bookmark.query.filter_by(url=url).first():
        return jsonify({
            "error": "URL already exists"
        }), HTTP_409_CONFLICT

    bookmark = Bookmark(url=url, body=body, user_id=current_user)
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({
        "id": bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_201_CREATED


@bookmarks.route("/<int:bookmark_id>", methods=["GET"])
@jwt_required()
@swag_from('./docs/bookmarks/get_bookmark.yaml')
def get_bookmark(bookmark_id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=bookmark_id).first()

    if not bookmark:
        return jsonify({
            "message": "Item not found"
        }), HTTP_404_NOT_FOUND

    return jsonify({
        "id": bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK


@bookmarks.route('/<int:bookmark_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@swag_from('./docs/bookmarks/put_patch_bookmark.yaml')
def edit_bookmark(bookmark_id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=bookmark_id).first()

    if not bookmark:
        return jsonify({
            "message": "Item not found"
        }), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            "error": "Enter a valid URL"
        }), HTTP_400_BAD_REQUEST

    bookmark.url = url
    bookmark.body = body
    db.session.commit()

    return jsonify({
        "id": bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK


@bookmarks.route("/<int:bookmark_id>", methods=["DELETE"])
@jwt_required()
@swag_from('./docs/bookmarks/delete_bookmark.yaml')
def delete_bookmark(bookmark_id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=bookmark_id).first()

    if not bookmark:
        return jsonify({
            "message": "Item not found"
        }), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.route("/stats", methods=['GET'])
@jwt_required()
@swag_from('./docs/bookmarks/stats.yaml')
def get_stats():
    current_user = get_jwt_identity()
    data = []

    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            "visits": item.visits,
            "url": item.url,
            "id": item.id,
            "short_url": item.url,
        }
        data.append(new_link)

    return jsonify({
        "data": data
    }), HTTP_200_OK
