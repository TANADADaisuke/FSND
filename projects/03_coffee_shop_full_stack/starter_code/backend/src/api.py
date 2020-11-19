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
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
GET /drinks
    it should be a public endpoint
    it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code
    indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    """Retrieve all drinks from database
    Arguments: None

    Returns: json {"success": True, "drinks": the list of drinks}
    """
    selection = Drink.query.all()
    drinks = []
    for drink in selection:
        drinks.append(drink.short())

    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code
    indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """Retrieve drinks detail from database. Access is limited.
    Arguments: HTTP request payload

    Returns: json {"success": True, "drinks": the list of drinks detail}
    """
    selection = Drink.query.all()
    drinks = []
    for drink in selection:
        drinks.append(drink.long())

    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):
    """Create new drink. Access is limited.
    Arguments: HTTP request payload

    Returns: json {"success": True, "drinks": created drink}
    """
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        print('title:', title, type(title))
        print('recipe:', recipe, type(recipe))
        # insert new drink
        if type(recipe) == list:
            new_drink = Drink(
                title=title,
                recipe=json.dumps(recipe)
            )
        else:
            new_drink = Drink(
                title=title,
                recipe=json.dumps([recipe])
            )
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })
    except Exception:
        abort(422)


'''
PATCH /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_detail(payload, drink_id):
    """Update drink recipe in our database. Access is limited.
    Arguments: HTTP request payload, drink_id

    Returns: json {"success":True, "drinks": updated drink}
             If drink_id is not found, abort 404
    """
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    try:
        if title is not None:
            drink.title = title
        if recipe is not None:
            if type(recipe) == list:
                drink.recipe = json.dumps(recipe)
            else:
                drink.recipe = json.dumps([recipe])

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        abort(422)


'''
DELETE /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row for <id>
    it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record or appropriate status code
    indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    """Delete the given drink. Access is limited.
    Arguments: HTTP request payload, drink_id

    Returns: json {"success": True, "delete": drink_id}
             If drink_id is not found, abort 404
    """
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id
    })


# Error Handling
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
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    message_code = error.error['code']
    print(message_code)
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['code']
    }), error.status_code
