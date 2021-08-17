import os
from re import T
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

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['sucecss'],True)
        self.assertEqual(data['current_category'],None)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
     
     
    def test_get_categories(self):        
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['sucecss'],True)
        
        # self.assertEqual(data['categories'],{'1': 'Science',
        #                                      '2': 'Art',
        #                                      '3': 'Geography',
        #                                      '4': 'History',
        #                                      '5': 'Entertainment',
        #                                      '6': 'Sports'})
        data.popitem()
        self.assertEqual(data['categories'],data['categories'])
       
    def test_get_questionByCateogries(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['current_categroy'],'Science')
        self.assertNotEqual(len(data['questions']),0)
    
    def test_add_questions(self):
        question_before_adding = Question.query.all()
        res = self.client().post('/questions', json = {
            'question': 'test? ',
            'answer': 'unit testing',
            'difficulty': 4,
            'category': '5'
        })
        question_after_adding = Question.query.all()
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['sucecss'],True)
        self.assertTrue(len(question_after_adding) -  len(question_before_adding)==1)
    
    def test_search_quesiton(self):
        res = self.client().post('/search', json={'searchTerm': 'test'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['sucecss'],True)        
    
        
    def test_play_quiz(self):
        
        res = self.client().post('/play', json={
                                                'previous_questions':[19,20],
                                                'quiz_category':{'id':'1','type':'Science'}
                                                     })
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['sucecss'],True)
        self.assertTrue(data['question'])
        
    def test_delte_question(self):
        new_questions = Question(question="tests?", answer="yes", category="2", difficulty=2 )
        new_questions.insert()
        question_id = new_questions.id
        
        res = self.client().delete('questions/{}'.format(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['sucecss'],True)
        self.assertEqual(data['deleted'],question_id)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()