import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError

from ma import ma
from blacklist import BLACKLIST
from db import db
from resources.user import (
    User,
    UserLogin,
    UserLogout,
    TokenRefresh,
    UserRegister
)
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.confirmatiom import Confirmation, ConfirmationByUser

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.secret_key = os.environ.get("APP_SECRET_KEY")  # app.config['JWT_SECRET_KEY']
api = Api(app)


@app.errorhandler(ValidationError)
def handle_marshmallow_bvalidation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)  # not creating /auth


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(header, decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    ma.init_app(app)
    app.run(debug=True)
