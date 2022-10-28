from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST
from db import db
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.secret_key = 'max' # app.config['JWT_SECRET_KEY']
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)  # not creating /auth

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:  # It should be red from db or config file
        return{'is_admin': True}
    return{'is_admin': False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(header, decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token is expired',
        'error': 'token_expired'
    }), 401
    
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token',
        'error': 'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is not fresh',
        'error': 'fresh_token_required'
    }), 401
    
@jwt.revoked_token_loader
def revoked_token_callback(header, error):
    return jsonify({
        'description': 'The token has been revoked',
        'error': 'token revoked'
    }), 401
    
api.add_resource(Store, '/store/<string:name>')    
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')


if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)