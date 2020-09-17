import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test for retrieving all available categories
    def test_retrieve_categories(self):
        '''Test retrieving all available categories'''
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_categories'], 6)
        self.assertEqual(len(data['categories']), 6)

    # test for retrieving paginated questions
    def test_retrieve_questions(self):
        '''Test retrieving paginated questions'''
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'], 19)
        self.assertTrue(data['current_category'])
        self.assertEqual(len(data['categories']), 6)

    # test 404 for retrieving over page questions
    def test_404_for_overpage_questions(self):
        '''Test 404 for overpage questions'''
        page = 100000
        res = self.client().get('/questions?page={}'.format(page))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')

    # test for delete the question
    def test_delete_question(self):
        '''Test deleting the question using question id'''
        delete_id = 5
        res = self.client().delete('/questions/{}'.format(delete_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], delete_id)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'], 19)
        self.assertTrue(data['current_category'])
        self.assertEqual(len(data['categories']), 6)

    # test 422 for delete against nonexist question
    def test_422_for_delete_against_nonexist_question(self):
        '''Test 422 for delete againse nonexist question'''
        delete_id = 100000
        res = self.client().delete('/questions/{}'.format(delete_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'umprocessable')

    # test creating a new question
    def test_create_question(self):
        res = self.client().post(
            '/questions', 
            json={
                'question': 'test question',
                'answer': 'test answer',
                'category': 4,
                'difficulty': 5
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'], 20)
        self.assertTrue(data['current_category'])
        self.assertEqual(len(data['categories']), 6)

    # test 422 for key less creation
    def test_422_for_keyword_less_creation(self):
        res = self.client().post(
            '/questions', 
            json={
                'question': 'test question',
                'category': 4,
                'difficulty': 5
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'umprocessable')
    
    # test searching questions based on a search term
    def test_search_questions(self):
        res = self.client().post('/questions', json={'searchTerm': 'what'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 8)
        self.assertEqual(data['total_questions'], 8)
        self.assertTrue(data['current_category'])
        self.assertEqual(len(data['categories']), 6)

    # test retrieving question accourding to their categories
    def test_retrieve_questions_by_category(self):
        category_id = 1
        res = self.client().get('/categories/{}/questions'.format(category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category']['id'], 1)
        self.assertEqual(len(data['categories']), 6)
    
    # test 404 for nonextist category
    def test_404_for_nonexist_category(self):
        category_id = 100000
        res = self.client().get('/categories/{}/questions'.format(category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')

    # test quizing
    def test_quiz(self):
        res = self.client().post(
            '/quizzes',
            json={
                'previous_questions': [],
                'quiz_category': {
                    'id': 1,
                    'type': 'Science'
                }
            }
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(type(data['question']), dict)
        self.assertEqual(data['current_category']['id'], 1)

    # test 405 for get method to retrieve quiz
    def test_405_for_get_method_against_quiz(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], 'method not allowed')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()