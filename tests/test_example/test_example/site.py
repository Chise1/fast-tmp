from test_example.models import Author, AuthorT, Book

from fast_tmp.admin.creator import AbstractApp, AbstractCRUD

app = AbstractApp(name="test-example", logo=None)
book_crud = AbstractCRUD(Book)
author_crud = AbstractCRUD(Author)
authorT_curd = AbstractCRUD(AuthorT)
app.add_page(book_crud)
app.add_page(author_crud)
app.add_page(authorT_curd)
