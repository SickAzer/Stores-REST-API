from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help='This field cannot be blank!'
    )
    parser.add_argument(
        'store_id',
        type=int,
        required=True,
        help='Every item needs a store id.'
    )

    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {'message': 'Item not found'}, 404
        
    @jwt_required(fresh=True)
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {'message': f'An item with name {name} already exists.'}, 400
        
        data = Item.parser.parse_args()
        
        item = ItemModel(name, **data)
        
        try:
            item.save_to_db()
        except:
            return {'message': 'An error occured inserting the item'}, 500
        
        return item.json(), 201
    
    @jwt_required()
    def delete(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item deleted'}, 200
        return {'message': 'Item not found'}, 404
    
    def put(self, name: str):
        data = Item.parser.parse_args()
        
        item = ItemModel.find_by_name(name)
        
        
        if item is None:
            item = ItemModel(name, **data)         
        else:
            item.price = data['price']
            
        item.save_to_db()
        
        return item.json()

class ItemList(Resource):
    def get(self):
        return {'items': [item.json() for item in ItemModel.find_all()]}, 200