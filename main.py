from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Your Secret key'
Bootstrap(app)

API_KEY = "Your API key"
URL = "https://api.themoviedb.org/3/search/movie"
URL_GET = f"https://api.themoviedb.org/3/movie/"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"


class EditForm(FlaskForm):
    rating = StringField(label='Your rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField(label='Your review', validators=[DataRequired()])
    submit = SubmitField(label='Done')

class AddForm(FlaskForm):
    title = StringField(label='Movie Title',validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Best_movies.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(350))
    img_url = db.Column(db.String(350), nullable=False)

db.create_all()

## After adding the new_movie the code needs to be commented out/deleted.
## So you are not trying to add the same movie twice.
#new_movie = Movie(
#    title="Phone Booth",
#    year=2002,
#    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#    rating=7.3,
#    ranking=10,
#    review="My favourite character was the caller.",
#    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#)
#db.session.add(new_movie)
#db.session.commit()

@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()
    n = len(movies)
    for movie in movies:
        movie.ranking = n
        n -= 1
    db.session.commit()
    return render_template("index.html", movies=movies)

@app.route('/edit',methods=['GET','POST'])
def edit():
    form = EditForm()
    id = request.args.get('id')
    movie_to_update = Movie.query.get(id)

    if request.method == "GET":
        return render_template("edit.html", movie=movie_to_update, form=form)

    #UPDATE RECORD
    movie_to_update.rating = float(request.form["rating"])
    movie_to_update.review = request.form["review"]
    db.session.commit()

    return redirect(url_for("home"))


@app.route('/delete',methods=['GET'])
def delete():
    id = request.args.get('id')
    # DELETE A RECORD BY ID
    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == "POST":
        movie_title = request.form["title"]
        response = requests.get(URL, params={"api_key": API_KEY, "query": movie_title})
        data_movies = response.json()["results"]
        return render_template("select.html", data=data_movies)

    form = AddForm()
    return render_template("add.html", form=form)

@app.route('/get')
def get():
    movie_id = request.args.get('id')
    if movie_id:
        response = requests.get(URL_GET+f"{movie_id}", params={"api_key": API_KEY})
        data_movie = response.json()
        # ADD RECORD
        new_movie = Movie(
            title=data_movie['title'],
            year=data_movie['release_date'].split('-')[0],
            description=data_movie['overview'],
            img_url=f"{IMAGE_URL}{data_movie['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == "__main__":
    app.run(debug=True)
