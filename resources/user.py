
import hmac
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from flask_restful import Resource, reqparse
from blacklist import BLACKLIST
from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    'username',
    type=str,
    required=True,
    help='This field cannot be blank!'
)
_user_parser.add_argument(
    'password',
    type=str,
    required=True,
    help='This field cannot be blank!'
)        

str_to_bytes = lambda s: s.encode("utf-8") if isinstance(s, str) else s
safe_str_cmp = lambda a, b: hmac.compare_digest(str_to_bytes(a), str_to_bytes(b))


class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()
        
        if UserModel.find_by_username(data['username']):
            return {'message': f'User with that name already exists.'}, 400
        
        user = UserModel(**data)
        user.save_to_db()
        
        return {"message": "User created successfully."}, 201
    

class User(Resource): 
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return{'message': 'User not found'}, 404
        return user.json()
    
    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return{'message': 'User not found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200
    

class UserLogin(Resource):

    @classmethod
    def post(self):
        # get data from parser
        data = _user_parser.parse_args()
        # find user in db
        user = UserModel.find_by_username(data['username'])
        # check password
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'message': 'Invalid credentials'}, 401
    
    
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {'messsage': 'Successfully logged out.'}, 200
    
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
    
    