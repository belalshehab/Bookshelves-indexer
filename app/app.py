import os
from flask import (Flask,
                   flash,
                   jsonify,
                   make_response,
                   redirect,
                   render_template,
                   request,
                   send_from_directory,
                   url_for)

from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MONGO_DBNAME'] = 'booksdb'
app.config['MONGO_URI'] = os.getenv('CONNECTION_URL')
mongo = PyMongo(app)

@app.route('/')
def Home():
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    return render_template('app.html')

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file_input']
        f.save(os.path.join(app.config["UPLOAD_FOLDER"], f.filename))
        #filePath = uploads/ + f.filename
        #function code to get list of dictionaries function(filePath)
        #book = mongo.db.books
        #bookIds = []
        # for book in bookList:
                #bookName = book['name']
                #author = book['author']
                #..........
                #book_id = book.insert({'name': name, 'lname':libraryName ,'author':author})
                #bookIds.append(book_id)

        booksList = []
        book = mongo.db.books
        name = f.filename
        libraryName = request.form['libraryname']
        author = 'john'
        book_id = book.insert({'name': name, 'lname':libraryName ,'author':author})
        return jsonify(str(book_id))


@app.route('/search', methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        if request.form['searchName']:
            bookName = request.form['searchName']
            book = mongo.db.books
            b_by_book = book.find_one({'name':bookName})
            bookObject = {'name':b_by_book['name'], 'library':b_by_book['lname']} # and so on to the end of schema
            return jsonify(bookObject)
        elif request.form['searchAuthor']:
            authorName = request.form['searchAuthor']
            book = mongo.db.books
            b_by_author = book.find({'author':authorName})
            booklist = []
            for b in b_by_author :
                bookObject = {'name':b['name'], 'library':b['lname']}
                booklist.append(bookObject)

            return jsonify(booklist)

        else:
            return 'error'



if __name__ == "__main__":
    app.debug = True
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))