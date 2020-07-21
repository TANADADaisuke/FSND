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
        self.assertEqual(len(data['current_questions']), 10)
        self.assertEqual(data['total_questions'], 18)
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
        self.assertEqual(len(data['current_questions']), 10)
        self.assertEqual(data['total_questions'], 18)
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
            '/question', 
            json={
                'question': 'test question',
                'answer': 'test answer',
                'category': 4,
                'difficulty': 5
            })
        data = json.loads(res.data)

        self.assertEqual(res.statuc_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['current_questions']), 10)
        self.assertEqual(data['total_questions'], 18)
        self.assertTrue(data['current_category'])
        self.assertEqual(len(data['categories']), 6)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()