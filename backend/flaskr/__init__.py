import os
from re import T
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
    page = request.args.get('page',1,type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','content-type,authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
          categories = Category.query.order_by(Category.type).all()
          if not categories:
              abort(422)
                
          return jsonify({
            "sucecss":True,
            "categories": {cat.id:cat.type for cat in categories}
          })
        except Exception as e:
          print(e)
          abort(404)
          
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
          questions = Question.query.all()
          current_questions = paginate_questions(request,questions)
          categories = Category.query.all()
          if (len(current_questions) == 0):
            abort(404)  
          return jsonify({
            "sucecss":True,
            "questions":current_questions,
            "total_questions": len(questions),
            "current_category":None,
            "categories": {cat.id:cat.type for cat in categories}
          })
        except Exception as e:
          print(e)
          abort(404)
          
    @app.route('/questions/<int:id>',methods=['DELETE'])
    def delete_question(id):
        question =  Question.query.filter( Question.id ==id).one_or_none()
        if not question:
              abort(404)
        try:
            question.delete()
            return jsonify({
                'sucecss':True,
                'deleted' :id})
            
        except Exception as e:
          print(e)
          abort(402)

    @app.route('/questions',methods=['POST'])
    def add_question():
        try:
          body = request.get_json()
          new_question = body.get('question')
          new_answer = body.get('answer')
          new_difficulty = body.get('difficulty')
          new_category = body.get('category')
          
          if ((new_question is None) or (new_answer is None) 
              or (new_difficulty is None) or (new_category is None)):
            abort(422)
    
          question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
          question.insert()
          
          return jsonify({
                'sucecss':True,
                'created' :question.id})
          
        except Exception as e:
          print(e)
          abort(422)
        
    @app.route('/search',methods=['POST'])
    def search_question():
        try:
          body = request.get_json()
          searchTerm = body.get('searchTerm')
          questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
          current_quesitons = paginate_questions(request,questions)
          total_questions = len(Question.query.all())
          category = Category.query.order_by(Category.id).all()

          if (len(questions) == 0) or not category:
              abort(404)
                  
          return jsonify({
              'sucecss':True,
              'questions': current_quesitons,
              'total_questions': total_questions,
              'current_categroy': category[0].format()['type']
            })
        except Exception as e:
          print(e)
          abort(404)
                  
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        try:
          category = Category.query.filter_by(id=id).one_or_none()
          selection = Question.query.filter_by(category=category.id).all()
          question_paginate = paginate_questions(request, selection)
          return jsonify({
                    'success':True,
                    'questions':question_paginate,
                    'total_questions': len(Question.query.all()),
                    'current_categroy': category.format()['type']})
        except Exception as e:
          print(e)
          abort(500)  
          
    @app.route('/play', methods=['POST'])
    def play_quiz():
        questions = None  
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')
    
        if ((previous_questions is None) or (category is None)):
              abort(400)
        try:
               
          if (category['id'] == 0):
            questions = Question.query.all()

          else:
            questions = Question.query.filter_by(category=category['id']).all()
            question = questions[random.randrange(0,len(questions),1)]
        
          # for q in questions:
          #   if q.id not in previous_questions:
          #     current_question = q.format()
          #     break
            
          return jsonify({
            'sucecss':True,
            'question': question.format()
          }) 
        except Exception as e:
          print(e)
          abort(400)  
      
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          'sucecss': False,
          'error': 404,
          'message': "resources not found"
        }),404
    
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          'sucecss': False,
          'error': 422,
          'message': "unprocessable"
        }),422
        
        
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          'sucecss': False,
          'error': 400,
          'message': "bad request"
        }),400
        
    @app.errorhandler(500)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500     
        
    if __name__ == '__main__':
        app.run(debug=True)
        
    return app

      