from test_example.models import Author, AuthorT, Book, Event, Team, Tournament

from fast_tmp.admin.creator import AbstractApp, AbstractCRUD
from fast_tmp.models import Group

app = AbstractApp(name="test-example", logo=None)
book_crud = AbstractCRUD(Book)
author_crud = AbstractCRUD(Author)
authorT_curd = AbstractCRUD(AuthorT)
app.add_page(book_crud)
app.add_page(author_crud)
app.add_page(authorT_curd)
event = AbstractCRUD(Event)
app.add_page(event)
team = AbstractCRUD(Team)
app.add_page(team)
tournament = AbstractCRUD(Tournament)
app.add_page(tournament)
group = AbstractCRUD(Group)
app.add_page(group)
