##--------------------------------------------------------##
'''
 REFERENCES: API development and documentation section of Full-Stack Developper nanodegree program
'''
##--------------------------------------------------------##
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
   CORS. Allow '*' for origins
  '''
  cors = CORS(app, resources={ r"/*": {"origins": "*"} })

  '''
   Using after_request decorator to set Access-Control-Allow for HEADERS: content-type, Authorization, METHODS: GET,POST,DELETE
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response

  '''
   SHOW ALL CATEGORIES
   Endpoint '/categories' : Handles GET requests for all available categories stored in the Category table. 
                            This endpoint returns success, total number of categores, list of categories 
                            Errors other than 422: None
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.all()
      format_categories = {}
      for cat in categories:
        format_categories[cat.id] = cat.type
      return jsonify({
           'success' : True,
           'total_categories': len(format_categories),
           'categories': format_categories
          } )
    except:
      abort(422)

  '''
   VIEW QUESTIONS IN PAGES
   Endpoint '/questions' : Handles GET requests for questions. It returns a paginated response with 10 questions per page and 
                           the page returned is based on input argument page, if page is not specified, page defaults to 1.
                           This end point returns {id, question, answer, category, difficulty} as questions for all the questions,
                           total number of questions in all pages as total_questions, categories. It also returns current_category
                           which can be ignored.
                           Errors other than 422: This endpoint returns not found(404) if the page specified in the argument doesn't exist.
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      page = request.args.get('page',1,type=int)
      start =  (page-1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      questions = Question.query.all()
      if start>=len(questions):
        raise NameError('abort404')
      format_questions = [quest.format() for quest in questions]
      categories = Category.query.all()
      format_categories = {}
      for cat in categories:
        format_categories[cat.id] = cat.type
      return jsonify({
        'questions': format_questions[start:end],
        'total_questions': len(format_questions),
        'categories': format_categories,
        'current_category': None 
        })
    except NameError:
      abort(404)
    except:
      abort(422)

  '''
   SEARCH QUESTIONS 
   Endpoint '/questions' : Handles POST requests for questions. It returns questions based on a searchTerm sent as part of POST request
                           in json format. This end point returns {id, question, answer, category, difficulty} as questions for all the 
                           questions containing the searchTerm, number of questions containing search term as total_questions. This search
                           is case-insensitive. It also returns current_category which can be ignored.
                           Errors other than 422: This endpoint returns bad request(400) if the searchTerm is not specified in the request.
                                                  This case is different from the searchTerm being empty.
  '''
  @app.route('/questions', methods=['POST'])
  def search_questions():
    try:
      new_term = request.get_json()
      if new_term is None:
        raise NameError('abort400')
      search_term = new_term['searchTerm']
      questions = Question.query.filter(func.lower(Question.question).like('%'+func.lower(search_term)+'%') ).all()
      format_questions = [quest.format() for quest in questions]
      return jsonify({
        'questions': format_questions,
        'total_questions': len(format_questions),
        'current_category': None
       })
    except NameError:
      abort(400)
    except:
      abort(422)
  
  '''
   DELETE QUESTION
   Endpoint '/questions/<question_id>' :  Handles DELETE requests for questions/<question_id>. Deletes the question with question_id as id.
                                          This end point returns success if question has been deleted successfully.
                                          Errors other than 422: This endpoint returns not found(404) if the question_id doesn't exist in the
                                          database.
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      del_question = Question.query.filter_by(id=question_id).first() 
      if del_question is None:
        raise NameError('abort404')
      del_question.delete()
      return jsonify({
        'success': True
        })
    except NameError:
      abort(404)
    except:
      abort(422)

  '''
   ADD A NEW QUESTION
   Endpoint '/addQuestion' : Handles POST requests for addQuestion. It returns success if the question has been added to the database 
                             successfully. It takes the input needed to add a new question from the POST request in the form of json.
                             The json input should contain question, answer, category, difficulty.
                             Errors other than 422: This endpoint returns bad request(400) if json input is not specified in the request.
                                                    If json input is empty, the category defaults to science, difficulty defaults to 1,
                                                    the question and answer fields are left empty.
  '''
  @app.route('/addQuestion', methods=['POST'])
  def add_question():
    try:
      json_question = request.get_json()
      if json_question is None:
        raise NameError('abort400')
      new_question = Question(question=json_question['question'],
                              answer=json_question['answer'],
                              category=json_question['category'],
                              difficulty=json_question['difficulty'])
      new_question.insert()
      return jsonify({
        'success': True
        })
    except NameError:
      abort(400)
    except:
      abort(422)

  '''
   VIEW QUESTIONS PER CATEGORY
   Endpoint '/categories/<category_id>/questions' : 
                           Handles GET requests for all questions for a specific category based on category_id from the endpoint.
                           This end point returns {id, question, answer, category, difficulty} as questions for specified category,
                           total number of questions as total_questions, category_id as current_category. 
                           Errors other than 422: This endpoint returns not found(404) if the category specified in the argument 
                                                  doesn't exist in the database.
  '''
  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      is_valid_category = Category.query.filter_by(id=category_id).first()
      if is_valid_category is None:
        raise NameError('abort404')
      questions = Question.query.filter_by(category=category_id).all()
      format_questions = [quest.format() for quest in questions]
      return jsonify({
        'questions': format_questions,
        'total_questions': len(format_questions),
        'current_category': category_id
        })
    except NameError:
      abort(404)
    except:
      abort(422)
 
  '''
   PLAY A QUIZ: GET NEXT QUESTION
   Endpoint '/quizzes': POST endpoint to '/quizzes' to get next question to play the quiz. It takes quiz category and previous questions
                        as input and returns a new question.
                        Errors other than 422: This endpoint returns bad request(400) if the json input is not given or if json input is 
                        not in a specific format. This case is different from an empty json input.
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz():
    try:
      quiz_info = request.get_json()
      if (quiz_info is None) or ('quiz_category' not in quiz_info) or ('id' not in quiz_info["quiz_category"]) or ('previous_questions' not in quiz_info):
        raise NameError('abort400')

      prev_category = quiz_info["quiz_category"] 
      prev_questions = quiz_info["previous_questions"]

      if prev_category['id'] == 0:
        new_question = Question.query.filter(~Question.id.in_(prev_questions)).first()
      else:
        new_question = Question.query.filter(Question.category==prev_category['id'],~Question.id.in_(prev_questions)).first()
      if new_question:
        new_question = new_question.format()
      return jsonify({
        'question': new_question
        })
    except NameError:
      abort(400)
    except:
      abort(422)
  
  '''
   Error Handlers for all expected errors
  '''
  @app.errorhandler(404) 
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not Found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message":"Unprocessable"
      }), 422
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message":"Method Not Allowed"
      }), 405

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message":"Request is incorrect, please check if request, data is correct"
      }), 400

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error":500,
      "message":"Something went wrong, please try again"
      }), 500

  return app

    