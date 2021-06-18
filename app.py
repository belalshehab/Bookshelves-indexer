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
from library_indedxer import indexer_wrapper, spot_the_book

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
        filePath = 'uploads/' + f.filename
        books = indexer_wrapper(filePath)

        books_list = []

        for book in books:
            book.library_url = filePath
            book.library_name = request.form['libraryname']
            book = book.__dict__()
            books_list.append(book)
        mongo.db.books.insert_many(books_list)
        return jsonify(str('success'))



@app.route('/search', methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        if request.form['searchName']:
            bookName = request.form['searchName']
            print(f'name: {bookName}')
            book = mongo.db.books
            b_by_book = book.find_one({'name': bookName})
            b_by_book['_id'] = ''

            b_by_book = spot_the_book(b_by_book)

            print(f'b_by_book: {b_by_book}')

            return jsonify(b_by_book)
        elif request.form['searchAuthor']:
            authorName = request.form['searchAuthor']
            book = mongo.db.books
            b_by_author = book.find({'author': authorName})
            booklist = []
            for b in b_by_author:
                bookObject = {'name': b['name'], 'library': b['lname']}
                booklist.append(bookObject)

            return jsonify(booklist)

        else:
            return 'error'


if __name__ == "__main__":
    app.debug = True
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
