class Book:
    def __init__(self):
        self.spine = None
        self.ocr_output = ''
        self.name = ''
        self.book_url = ''
        self.library = ''
        self.shelf = ''
        self.index = ''
        self.bounding_rectangle = ((0, 0), (0, 0))

    def __dict__(self):
        return {
            'spine': self.spine.shape,
            'ocr_output': self.ocr_output,
            'name': self.name,
            'book_url': self.book_url,
            'library': self.library,
            'shelf': self.shelf,
            'index': self.index,
            'bounding_rectangle': self.bounding_rectangle
        }

    def __str__(self):
        return f'Book->{self.__dict__()}'

    def __repr__(self):
        return str(self)

