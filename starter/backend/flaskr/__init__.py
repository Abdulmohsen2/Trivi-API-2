import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
NUMBER_OF_PAGE = 1


def get_paginated_questions(request, selections):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE

    Questions = [question.format() for question in selections]
    CurrQuestions = Questions[start:end]

    return CurrQuestions


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={'/': {'origins': '*'}})

    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        try:

            categoriesData = Category.query.all()
            categories = {}
            for category in categoriesData:
                categories[category.id] = category.type

            return jsonify({
                'success': True,
                'categories': categories
            })
        except:
            abort(404)

    @app.route('/questions')
    def retrieve_questions():
        try:
            GetQuestion = Question.query.order_by(Question.id).all()
            categoriesData = Category.query.all()

            currQuestion = get_paginated_questions(
                request, GetQuestion)

            categories = {}
            for category in categoriesData:
                categories[category.id] = category.type

            if (len(currQuestion) == 0):
                abort(404)

            return jsonify({
                'success': True,
                'questions': currQuestion,
                'total_questions': len(GetQuestion),
                'categories': categories
            })
        except:
            abort(404)

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            GetQuestion = Question.query.get(id)
            if (GetQuestion == ""):
                abort(422)
            GetQuestion.delete()

            if GetQuestion is None:
                abort(422)
            return jsonify({
                'success': True,
                'message': "Deleted!"
            }), 200
        except:
            abort(422)

    @app.route("/questions", methods=['POST'])
    def Addearch_question():

        try:
            Info = request.get_json()
            search = Info.get('searchTerm')
            if search:
                questions = Question.query.filter(Question.question.ilike(
                    f'%{search}%')).order_by(Question.difficulty).all()
                paginated = get_paginated_questions(request, questions)
                return jsonify({
                    "success": True,
                    'questions': paginated,
                    'total_questions': len(questions),

                })
            else:
                question = Info['question']
                answer = Info['answer']
                difficulty = Info['difficulty']
                category = Info['category']
                if (len(question) == 0) or (len(answer) == 0):
                    abort(422)
                question = Question(question=question, answer=answer,
                                    difficulty=difficulty, category=category)
                question.insert()
                length_of_question = len(Question.query.all())
                return jsonify({
                    "success": True,
                    "created": question.id,
                    "message": "question is added",
                    "total_question": length_of_question
                })
        except:
            abort(422)

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):

        try:
            category = Category.query.get(id)
            if category is None:
                abort(404)
            questionsCategory = Question.query.order_by(Question.id).filter_by(
                category=id).all()
            if questionsCategory is None:
                abort(404)
            questions_page = get_paginated_questions(
                request, questionsCategory)

            if (questionsCategory == ''):
                abort(404)

            total = len(questionsCategory)
            return jsonify({
                "success": True,
                "questions": questions_page,
                "current_category": id,
                "total_questions": total

            })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        try:
            data = request.get_json()
            previous_questions = data.get('previous_questions')
            quiz_category = data.get('quiz_category')
            category_id = int(quiz_category["id"])
            next_question = ""

            if ((quiz_category == "") or (previous_questions == "")):
                abort(400)

            if category_id == 0:
                play_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                play_questions = Question.query.filter_by(category=category_id).filter(
                    Question.id.notin_((previous_questions))).all()
            lne = len(play_questions)
            if lne > 0:
                next_question = random.choice(play_questions).format()

            if(next_question == None):
                abort(422)

            return jsonify({
                'question': next_question,
                'success': True,
            })
        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
