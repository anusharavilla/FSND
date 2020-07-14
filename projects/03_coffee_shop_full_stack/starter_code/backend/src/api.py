'''
    REFERENCES: API development and documentation section of Udacity Full stack nano degree program
'''
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()


'''
Endpoint: GET /drinks
        Description:         This method returns the list of all drinks in the database, it doesn't include the entire recipe
        Permission:          no permission required.
        Data Representation: Returns only the drink.short() data representation
        Return data format:  Returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks 
                             or appropriate status code indicating reason for failure
'''
## ROUTES
@app.route('/drinks', methods=['GET'])
def drinks_short():
    drinks_formatted = []
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        if len(drinks)!=0:
            drinks_formatted = [drink.short() for drink in drinks]
        return jsonify ({
            'success' : True,
            'drinks'  : drinks_formatted 
        })
    except:
        abort(422)

'''
Endpoint: GET /drinks-detail
        Description:         This method returns the list of all drinks with recipes in the database
        Permission:          'get:drinks-detail' permission required.
        Data Representation: Returns the drink.long() data representation
        Return data format:  Returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks 
                             or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_long(payload):
    drinks_formatted = []
    try:
        drinks = Drink.query.all()
        if len(drinks)!=0:
            drinks_formatted = [drink.long() for drink in drinks]
        return jsonify ({
            'success' : True,
            'drinks'  : drinks_formatted
        })
    except:
        abort(422)

'''
Endpoint: POST /drinks
        Description:         This method adds a new drink with new information from user and returns the newly added drink information.
        Permission:          'post:drinks' permission required.
        Data Representation: Returns the drink.long() data representation
        Return data format:  Returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
                             or appropriate status code indicating reason for failure
        Failure cases:       Responds with a 400 error if input is not given      
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def drinks_post(payload):
    try:
        input_drink = request.get_json()
        if input_drink is None:
            raise NameError('abort400')
        new_drink = Drink(title=input_drink['title'],recipe=json.dumps(input_drink['recipe']))
        new_drink.insert()
        added_drink = Drink.query.filter_by(title=new_drink.title).first()
        drinks_formatted = [added_drink.long()]
        return jsonify ({
            'success' : True,
            'drinks'  : drinks_formatted 
        })
    except NameError:
        abort(400)
    except:
        abort(422)

'''
Endpoint: PATCH /drinks/<id> , where <id> is the id of the drink
        Description:         This method updates the drink with id=<id> with new information from user and returns the updated information.
        Permission:          'patch:drinks' permission required.
        Data Representation: Returns the drink.long() data representation
        Return data format:  Returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
                             or appropriate status code indicating reason for failure
        Failure cases:       Responds with a 404 error if <id> is not found        
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def drinks_patch(id,payload):
    try:
        input_drink = request.get_json()
        drink = Drink.query.filter_by(id=id).one_or_none()
        if not drink:
            raise NameError('abort404')
        if 'title' in input_drink:
            drink.title = input_drink['title']
        if 'recipe' in input_drink:
            drink.recipe = json.dumps(input_drink['recipe'])
        drink.update()
        updated_drink = Drink.query.filter_by(id=id).one_or_none()
        drinks_formatted = [updated_drink.long()]
        return jsonify ({
            'success' : True,
            'drinks'  : drinks_formatted 
        })
    except NameError:
        abort(404)
    except:
        abort(422)

'''
Endpoint: DELETE /drinks/<id>, where <id> is the id of the drink
        Description:         This method deletes the drink with id=<id> in the database and returns the deleted id.
        Permission:          'delete:drinks' permission required.
        Data Representation: Returns the drink.long() data representation
        Return data format:  Returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
                             or appropriate status code indicating reason for failure
        Failure cases:       Responds with a 404 error if <id> is not found        
'''    
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def drinks_delete(id,payload):
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if not drink:
            raise NameError('abort404')
        drink.delete()
        return jsonify ({
            'success' : True,
            'delete'  : id
        })
    except NameError:
        abort(404)
    except:
        abort(422)

'''
 Error Handlors for all expected errors
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Resource Not Found"
                    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
                    "success": False, 
                    "error": 405,
                    "message": "Method Not Allowed"
                    }), 405

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "Bad request, check the input data format"
                    }), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "Internal Server Error"
                    }), 500


@app.errorhandler(AuthError)
def auth_error_handler(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

