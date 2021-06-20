# Bookshelves-indexer

# DarkRectangle Manging your library !

## How to open the app:
### 1. from source code:
1. Download all required dependencies with this pip install -r requirements.txt.

2. Run the app with this python3 app.py

3. Go to this http://127.0.0.1:5000/

### 2. use executable:
1. run Bookshelves-indexer.exe
2. Go to this http://127.0.0.1:5000/

## How to Generate EXE:
run this in the command line:
`pyinstaller -n Bookshelves_indexer --add-data="templates/;templates/" --add-data="uploads/;uploads/" --add-data="static/;static/" --add-data="co
nfig.json;config.json" app.py`
