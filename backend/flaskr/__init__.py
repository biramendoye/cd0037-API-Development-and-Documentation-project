import random

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from models import Category, Question, setup_db
from utils import paginate_resources

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, origins="*")

    """
    Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )

        return response

    @app.route("/categories", methods=["GET"])
    def get_categories():
        """Create an endpoint to handle GET requests for all available categories."""
        data = {}
        categories = Category.query.order_by(Category.id).all()
        for category in categories:
            data[category.id] = category.type

        return jsonify(
            {
                "success": True,
                "categories": data,
            }
        )

    @app.route("/questions", methods=["GET"])
    def get_questions():
        """
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions, number of total questions, current category, categories.
        """
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_resources(request, selection, QUESTIONS_PER_PAGE)

        if len(current_questions) == 0:
            abort(404)
        else:
            current_category = Category.query.filter(
                Category.id == current_questions[0]["category"]
            ).first()

        data = {}
        categories = Category.query.order_by(Category.id).all()
        for category in categories:
            data[category.id] = category.type

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "current_category": current_category.type,
                "categories": data,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """Create an endpoint to DELETE question using a question ID."""
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
            else:
                question.delete()
                return jsonify(
                    {
                        "success": True,
                        "deleted": question_id,
                    }
                )
        except:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_new_question():
        """
        Create an endpoint to POST a new question, which will require the question and answer text,  category, and difficulty score.
        Create a POST endpoint to get questions based on a search term which will require the search term.
        """
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)
        search_term = body.get("searchTerm", None)
        category_type = body.get("type", None)

        try:
            if search_term:
                selection = (
                    Question.query.order_by(Question.id)
                    .filter(Question.question.ilike(f"%{search_term}%"))
                    .all()
                )
                current_questions = paginate_resources(
                    request, selection, QUESTIONS_PER_PAGE
                )

                current_category = Category.query.filter(
                    Category.id == current_questions[0]["category"]
                ).first()

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection),
                        "current_category": current_category.type,
                    }
                )
            elif question and answer and difficulty and category:
                new_question = Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category,
                )
                new_question.insert()

                return jsonify(
                    {
                        "success": True,
                    }
                )
            elif category_type:
                category = Category.query.filter(
                    Category.type.ilike(f"%{category_type}%")
                ).one_or_none()
                if category is None:
                    abort(404)
                else:
                    selection = Question.query.filter(
                        Question.category == category.id
                    ).all()
                    current_questions = paginate_resources(
                        request, selection, QUESTIONS_PER_PAGE
                    )

                    return jsonify(
                        {
                            "success": True,
                            "questions": current_questions,
                            "total_questions": len(selection),
                            "current_category": category.type,
                        }
                    )
            else:
                abort(400)
        except:
            abort(422)

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_from_category(category_id):
        """Create a GET endpoint to get questions based on category."""
        try:
            category = Category.query.filter(Category.id == category_id).one_or_none()

            if category is None:
                abort(404)
            else:
                selection = Question.query.filter(
                    Question.category == category_id
                ).all()
                current_questions = paginate_resources(
                    request, selection, QUESTIONS_PER_PAGE
                )

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection),
                        "current_category": category.type,
                    }
                )
        except:
            abort(400)

    @app.route("/quizzes", methods=["POST"])
    def get_quizzes():
        """
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.
        """
        body = request.get_json()
        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        # in the frontend quiz_category is a dict like {'type: 'History', 'id': 4}
        try:
            if quiz_category is None:
                selection = Question.query.filter(
                    ~Question.id.in_(previous_questions),
                ).all()
            else:
                selection = Question.query.filter(
                    ~Question.id.in_(previous_questions),
                    Question.category == quiz_category["id"],
                ).all()

            current_questions = paginate_resources(
                request, selection, QUESTIONS_PER_PAGE
            )
            random_question = random.choice(current_questions)

            return jsonify(
                {
                    "success": True,
                    "question": random_question,
                }
            )
        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        """Create error handlers for 404"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def not_found(error):
        """Create error handlers for 405"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 405,
                    "message": "Method Not Allowed",
                }
            ),
            405,
        )

    @app.errorhandler(400)
    def bad_request(error):
        """Create error handlers for 400"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "bad request",
                }
            ),
            400,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        """Create error handlers for 422"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 422,
                    "message": "unprocessable",
                }
            ),
            422,
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Create error handlers for 500"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "internal error",
                }
            ),
            500,
        )

    return app
