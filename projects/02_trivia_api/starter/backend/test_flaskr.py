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
        self.database_path = "postgres://{}/{}".format('username:password@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    def test_405_categories_method_not_alllowed(self):
        res = self.client().post('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['message'],'Method Not Allowed')

    def test_200_get_categories(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'],True)
        self.assertTrue(data['total_categories'],True)

    def test_404_page_does_not_exist(self):
        res = self.client().get('/questions?page=100')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')
    
    def test_200_questions_per_page(self):
        res = self.client().get('/questions?page=1')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'],True)
        self.assertTrue(data['categories'],True)
        self.assertTrue(data['questions'],True)

    def test_404_delete_question_not_found(self):
        res=self.client().delete('/questions/1000')  
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')

    def test_200_delete_successful(self):
        res=self.client().delete('/questions/1') # might fail after first deletion
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_400_add_question_data_not_specified(self):
        res=self.client().post('/addQuestion')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)
        self.assertEqual(data['message'],'Request is incorrect, please check if request, data is correct')

    def test_200_addQuestion(self):
        res=self.client().post('/addQuestion',json={"question": "New", "answer":"newnew", "category":"6", "difficulty":"2"})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_422_bad_question_add_data(self):
        res=self.client().post('/addQuestion',json={"question": "New", "answer":"newnew", "category":"6"})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertEqual(data['message'],'Unprocessable')        

    def test_400_searchTerm_not_specified(self):
        res=self.client().post('/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)
        self.assertEqual(data['message'],'Request is incorrect, please check if request, data is correct')
        
    def test_200_searchTerm(self):
        res=self.client().post('/questions',json={"searchTerm": "Africa"})
        self.assertEqual(res.status_code,200)
        data=json.loads(res.data)
        self.assertTrue(data['total_questions'],True)
        self.assertTrue(data['questions'],True)

    def test_422_bad_searchTerm(self):
        res=self.client().post('/questions',json={"searchTerm": {"Africa":1}})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertEqual(data['message'],'Unprocessable')        

    def test_404_category_not_found(self):
        res=self.client().get('/categories/100/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')
    
    def test_200_questions_per_category(self):
        res=self.client().get('/categories/1/questions')
        self.assertEqual(res.status_code,200)
        data=json.loads(res.data)
        self.assertTrue(data['questions'],True)
        self.assertTrue(data['total_questions'],True)
        self.assertTrue(data['current_category'],True)
            
    def test_405_quizzes_method_not_alllowed(self):
        res = self.client().get('/quizzes')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['message'],'Method Not Allowed')

    def test_400_quizzes_input_json_not_given(self):
        res = self.client().post('/quizzes')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)
        self.assertEqual(data['message'],'Request is incorrect, please check if request, data is correct')
        
    def test_400_quizzes_bad_json_input_given(self):
        res=self.client().post('/quizzes', json={"previous_questions":[20]})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)
        self.assertEqual(data['message'],'Request is incorrect, please check if request, data is correct')

    def test_200_quizzes(self):
        res = self.client().post('/quizzes', json={"quiz_category":{"id":"1"}, "previous_questions":[20]})
        self.assertEqual(res.status_code,200)
        data=json.loads(res.data)
        self.assertTrue(data['question'],True)
        self.assertTrue(data['question']['answer'],True)
        self.assertTrue(data['question']['category'],True)
        self.assertTrue(data['question']['difficulty'],True)
        self.assertTrue(data['question']['id'],True)
        self.assertTrue(data['question']['question'],True)

    def test_422_quizzes(self):
        res = self.client().post('/quizzes', json={"quiz_category":{"id":"1"}, "previous_questions":"2,3"})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],422)
        self.assertEqual(data['message'],'Unprocessable')        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()


'''
TODO remove your password in db before submitting
'''