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
    
        self.new_question = {
            'question': 'Which four states make up the 4 Corners region of the US?',
            'answer': 'Colorado, New Mexico, Arizona, Utah',
            'difficulty': 3,
            'category': '3'
        }
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["sucecss"], True)

        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
        
    def test_request_paginate_beyond_valid_page(self):
        
        res = self.client().get('/questions?page=10000',json={"rating":1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["sucecss"],False)
        self.assertEqual(data['message'],'resources not found')
    
    
    def test_delete_question(self):
        
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],difficulty=self.new_question['difficulty'],category=self.new_question['category'])
        question.insert()
        
        question_id = question.id
        
        question_before_delete = question.query.all() 
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)
        
        question_after_delete = question.query.all() 
        
        #  check if it has been deleted
        question = Question.query.filter( Question.id == 1).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["sucecss"], True)
        self.assertEqual(data['deleted'], question_id)
        
        self.assertTrue(len(question_before_delete) - len(question_after_delete) == 1)

        self.assertEqual(question, None)
     
     
    def test_insert_new_question(self):   
        
        question_before_insert = Question.query.all()
        res = self.client().post('/questions', json = self.new_question)
        data = json.loads(res.data)
        question_after_insert = Question.query.all()
        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["sucecss"],True)
        
        self.assertTrue(len(question_after_insert)  - len(question_before_insert)== 1)
        
        self.assertIsNotNone(question)
        
        
    def test_422_if_question_creation_fail(self):
           
        questions_before_create = Question.query.all()
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        questions_after_create = Question.query.all()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["sucecss"], False)
        self.assertEqual(data['message'], "unprocessable")
        
        
    def test_search_questions(self):

        res = self.client().post('/questions/search',json={'searchTerm': 'egyptians'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['sucecss'], True)
        
        self.assertEqual(len(data['questions']), 1)

        self.assertEqual(data['questions'][0]['id'], 23)


    def test_422_if_search_questions_fail(self):

        res = self.client().post('/questions/search', json={'searchTerm': 'abcdefghijk'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['sucecss'], False)
        self.assertEqual(data['message'], "resources not found")
        
        
    def test_get_questions_by_category(self):
        
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 1)
    
        self.assertEqual(data["current_categroy"], None)
    
    def test_404_if_questions_by_category_fail(self):
       
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['sucecss'], False)
        self.assertEqual(data['message'],  'bad request')

    
    def test_play_quiz_game(self):
        
        res = self.client().post('/play',json={'previous_questions': [20, 21],'quiz_category': {'type': 'Science', 'id': '1'}})
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['sucecss'], True)
       
   

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()