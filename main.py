import flask
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "adoijkloijafdljks"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///book-library.sqlite-3"
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

# Books Database
class Books(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("Book Title", db.String(250), unique=True, nullable=False)
    author = db.Column("Author", db.String(250), nullable=False)
    rating = db.Column("Rating", db.String, nullable=False)
    def __init__(self, title, author, rating):
        self.title = title
        self.author = author
        self.rating = rating
    def __repr__(self):
        return f"{self.title} by {self.author}: {self.rating}"

# To Read Database
class BooksToRead(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("Book Title", db.String(250), unique=True, nullable=False)
    author = db.Column("Author", db.String(250), nullable=False)
    def __init__(self, title, author):
        self.title = title
        self.author = author
    def __repr__(self):
        return f"{self.title} by {self.author}"

# Create Forms
class BooksForm(FlaskForm):
    title_input = StringField(label="Book Title", validators=[DataRequired("Please enter a book title.")])
    author_input = StringField(label="Author", validators=[DataRequired("Please enter an author.")])
    rating_input = SelectField(label="Rating", choices=[("★"), ("★★"), ("★★★"), ("★★★★"), ("★★★★★")])

class ToRead(FlaskForm):
    title_input = StringField(label="Book Title", validators=[DataRequired("Please enter a book title.")])
    author_input = StringField(label="Author", validators=[DataRequired("Please enter an author.")])

class EditRating(FlaskForm):
    rating_input = SelectField(label="Rating", choices=[("★"), ("★★"), ("★★★"), ("★★★★"), ("★★★★★")], validators=[DataRequired("Please select a rating.")])

# Create Database
db.create_all()

@app.route('/')
def home():
    finished_books = db.session.query(Books).all()
    to_read = db.session.query(BooksToRead).all()
    return render_template("index.html", book_list=finished_books, to_read=to_read)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = BooksForm()
    db.session.flush()
    if flask.request.method == "POST":
        entry = Books(title=form.title_input.data, author=form.author_input.data, rating=(form.rating_input.data))
        db.session.add(entry)
        db.session.commit()
    if form.validate_on_submit():
        return redirect(url_for("home"))
    return render_template("add.html", form=form)

@app.route("/add-to-read", methods=["GET", "POST"])
def add_to_read():
    form = ToRead()
    db.session.flush()
    if flask.request.method == "POST":
        entry = BooksToRead(title=form.title_input.data, author=form.author_input.data)
        db.session.add(entry)
        db.session.commit()
    if form.validate_on_submit():
        return redirect("/")
    return render_template("to_read.html", form=form)

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    form = EditRating()
    book_to_update = Books.query.get(id)
    if flask.request.method == "POST":
        book_to_update.rating = form.rating_input.data
        db.session.commit()
    if form.validate_on_submit():
        return redirect("/")
    return render_template("edit.html", form=form, id=id, book=book_to_update)

@app.route("/delete/<id>", methods=["GET", "POST"])
def delete(id):
    book_to_delete = Books.query.get(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect("/")

@app.route("/delete-to-read/<id>", methods=["GET","POST"])
def delete_to_read(id):
    book_to_delete = BooksToRead.query.get(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
