# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 




## Endpoints - required info

Return which includes categories will return categories in the following format for all endpoints:
CATEGORY FORMAT FOR ALL ENDPOINTS: An object with a single key, categories, that contains a object of id: category_string key:value pairs
    {'1' : "Science",
     '2' : "Art",
     '3' : "Geography", 
     '4' : "History",
     '5' : "Entertainment",
     '6' : "Sports"}

Return which includes questions will return questions in the following format for all endpoints:
QUESTION FORMAT:  An object with a keys 'id', 'question', 'category', 'difficulty' that contains a object of id: category_string key:value pairs
     {'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty}

## Endpoints

GET '/categories' : SHOW ALL CATEGORIES
                - Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
                - Request Arguments: None
                - Returns: An object with key value pairs { 'categories': CATEGORY FORMAT mentioned above, 'success': T/F, 'total_categories': number of total categories } 
                - Errors other than 422: None

GET '/questions'  : VIEW QUESTIONS IN PAGES
                - Fetches a paginated response with 10 questions per page based on input argument page
                - Request agruments: page number as page, integer. Defaults to 1.
                - Returns an object with key value pairs { 'questions': list of QUESTION FORMAT, 'total_questions': number_of_questions(number), 'categories': CATEGORY FORMAT, current_category(ignore): None}.
                - Errors other than 422: This endpoint returns not found(404) if the page specified in the argument doesn't exist.

POST '/questions' : SEARCH QUESTIONS 
                - Fetches questions based on a searchTerm. 
                - Request arguments: SearchTerm string, defaults to ''
                - Returns an object with key value pairs { 'questions' list of QUESTION FORMAT, 'total_questions': number_of_questions_with_search_term(number)}. This search is case-insensitive. It also returns current_category which can be ignored.
                - Errors other than 422: This endpoint returns bad request(400) if the searchTerm is not specified in the request.
                                         This case is different from the searchTerm being empty.

DELETE '/questions/<question_id>' : DELETE QUESTION
                - Handles DELETE requests for to question with id question_id. 
                - Request arguments: None
                - Deletes the question with question_id as id. This end point returns success if question has been deleted successfully.
                - Errors other than 422: This endpoint returns not found(404) if the question_id doesn't exist in the database.

POST '/addQuestion': ADD A NEW QUESTION
                - Handles adding a new question into the database. 
                - Request arguments: An object with question(string), answer(string), category(string), difficulty(string)
                - Returns success if the question has been added to the database successfully.
                - Errors other than 422: This endpoint returns bad request(400) if json input is not specified in the request.
                                         If json input is empty, the category defaults to science, difficulty defaults to 1, the question and answer fields are left empty.


GET '/categories/<category_id>/questions':  VIEW QUESTIONS PER CATEGORY
                - Handles GET requests for all questions for a specific category based on category_id from the endpoint.
                - Request Arguments: None
                - Returns an object with key value pairs {questions: list of QUESTION CATEGORY, 'total_questions': total number of questions, 'current_category': category_id(string)  }
                - Errors other than 422: This endpoint returns not found(404) if the category specified in the argument 
                                                  doesn't exist in the database.
  
POST '/quizzes':  PLAY A QUIZ: GET NEXT QUESTION
                - Handles get next question to play the quiz.
                - Request Arguments quiz_category(dtring) and previous_questions(string).
                - returns an object with a random new question in QUESTION FORMAT.
                - Errors other than 422: This endpoint returns bad request(400) if the json input is not given or if json input is 
                        not in a specific format. This case is different from an empty json input.


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```



##-------------------------------------------------------------------------------------------------------------------------##
## Guidelines for writing the document
## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 
