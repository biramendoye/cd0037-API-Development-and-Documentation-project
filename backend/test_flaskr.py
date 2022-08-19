import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question
from dotenv import load_dotenv


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and init.ialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        load_dotenv()
        username = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASSWORD")
        host = os.environ.get("DB_HOST", default="localhost")
        port = os.environ.get("DB_PORT", default=5432)
        self.database_path = "postgresql://{}:{}@{}:{}/{}".format(
            username, password, host, port, self.database_name
        )
        setup_db(app=self.app, database_path=self.database_path)

        self.new_question = {
            "question": "Who hosts the family feud TV show ?",
            "answer": "Steve Harvey",
            "difficulty": 2,
            "category": "5",
        }

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
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])

    def test_get_questions_successfully(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(data["categories"])

    def test_404_invalide_page_number(self):
        res = self.client().get("/questions?page=256")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted"])
        self.assertEqual(question, None)

    def test_delete_an_inexistant_question(self):
        res = self.client().delete("/questions/581322897")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_post_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_unprocessable_create_new_question(self):
        res = self.client().post("/questions", json={"question": "I have no answer ?"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_question(self):
        res = self.client().post("/questions", json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

    def test_get_questions_based_on_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

    def test_invalid_category_id(self):
        res = self.client().get("/categories/58132144/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_quizzes(self):
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [1, 2, 3, 4],
                "quiz_category": {"type": "History", "id": 4},
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])

    def test_unprocessable_quizzes(self):
        res = self.client().post(
            "/quizzes",
            json={
                "quiz_category": {"type": "History", "id": 4},
            },
        )

        self.assertEqual(res.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
