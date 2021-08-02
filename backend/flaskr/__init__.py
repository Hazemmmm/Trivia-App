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
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

  
  
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','content-type,authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        
        return response


#  GET Categroies & Questions
      
    @app.route('/categories', methods=['GET'])
    def get_categories():
          
        try:
          categories = Category.query.order_by(Category.type).all()
      
        
          return jsonify({
            "sucecss":True,
            "categories": {
              category.id:category.type for category in categories
            }
          })
          
        except:
          abort(500)


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
            "categories": {
              category.id:category.type for category in categories
            }
          })
          
        except:
          abort(404)

 # DELETE Question by id
    @app.route('/questions/<int:id>',methods=['DELETE'])
    def delete_question(id):
        question =  Question.query.filter( Question.id ==id).one_or_none()
        if question:
            try:
              question.delete()
            
              return jsonify({
                  'sucecss':True,
                  'deleted' :id
              })
            
            except:
              abort(402)
        abort(404)
                    
# ADD New Question
    @app.route('/questions',methods=['POST'])
    def add_question():
        try:
          body = request.get_json()
          new_question = body.get('question')
          new_answer = body.get('answer')
          new_difficulty = body.get('difficulty')
          new_category = body.get('category')
          
          question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
          question.insert()
          
          return jsonify({
                'sucecss':True,
                'created' :question.id
            })
            
        except:
            abort(422)
                   
# Search for Exisiting Questions.
    @app.route('/questions/search',methods=['POST'])
    def search_question():
          
          try:  
            body = request.get_json()
            search_term = body.get('searchTerm',None)
            if search_term:
                  search_result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
                  
                  return jsonify({
                    'sucecss':True,
                    'questions': [question.format() for question in search_result],
                    'total_questions': len(search_result),
                    'current_categroy': None
                  })
                  
          except:
            abort(422)        

#GET Questions based on Category Id
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        
        try:
          
          questions = Question.query.filter(Question.category == id).all()
          
          return jsonify({
            'success':True,
            'questions':[question.format() for question in questions],
            'total_questions': len(questions),
            'current_categroy':None
          })
          
        except:
          abort(404)



 
    
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

      