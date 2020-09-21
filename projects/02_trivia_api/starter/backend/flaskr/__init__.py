import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    cors = CORS(app, resource={r'*': '*'})

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start: end]

        return current_questions

    def current_category(request):
        category_id = request.args.get('category', 1, type=int)
        selection = Category.query.get(category_id)
        category = selection.format()

        return category

    def response_categories():
        selection = Category.query.all()
        categories = [category.format() for category in selection]
        response = {}
        for category in categories:
            response[category['id']] = category['type']

        return response

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Autorization, true'
            )
        response.headers.add(
            'Access-Control-Allow-Methos',
            'GET, POST, PATCH, DELETE, OPTIONS'
            )
        return response

    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.all()
        categories = response_categories()

        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    @app.route('/questions')
    def retrieve_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        else:
            selection = Category.query.order_by(Category.id).all()
            categories = response_categories()
            category = current_category(request)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category,
                'categories': categories
            })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(422)

            question.delete()

            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            selection = Category.query.order_by(Category.id).all()
            categories = response_categories()
            category = current_category(request)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category,
                'categories': categories
            })
        except:
            print(sys.exc_info())
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()
            search = body.get('searchTerm', None)
            if search:
                questions = Question.query.\
                    filter(Question.question.ilike('%{}%'.format(search))).\
                    order_by(Question.id).all()
                current_questions = paginate_questions(request, questions)

                selection = Category.query.order_by(Category.id).all()
                categories = response_categories()
                category = current_category(request)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions),
                    'current_category': category,
                    'categories': categories
                })
            else:
                new_question = body['question']
                new_answer = body['answer']
                new_category = body['category']
                new_difficulty = body['difficulty']
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty
                )
                question.insert()

                questions = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, questions)

                selection = Category.query.order_by(Category.id).all()
                categories = response_categories()
                category = current_category(request)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(questions),
                    'current_category': category,
                    'categories': categories
                })
        except:
            print(sys.exc_info())
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).\
            order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)
        else:
            selection = Category.query.order_by(Category.id).all()
            categories = response_categories()
            category = Category.query.get(category_id).format()

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category,
                'categories': categories
            })

    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        category = body.get('quiz_category', {'id': 0, 'type': 'click'})

        if category['id'] == 0:
            selection = Question.query.all()
        else:
            selection = Question.query.\
                filter(Question.category == category['id']).all()

        questions = [question.format() for question in selection]
        if len(questions) == len(set(previous_questions)):
            current_question = False
        else:
            selection_without_previous = []
            for question in questions:
                if question['id'] in previous_questions:
                    continue
                else:
                    selection_without_previous.append(question)

            current_question = random.choice(selection_without_previous)

        return jsonify({
            'success': True,
            'question': current_question,
            'current_category': category,
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'not found'
        }), 404

    @app.errorhandler(422)
    def umprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'umprocessable'
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    return app
