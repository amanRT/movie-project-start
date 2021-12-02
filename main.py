from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

MOVIE_ENDPOINT="https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
API_KEY="63498a250767f564ebc2c89b0942e315"
class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    movie= StringField("Movie Name")
    submit = SubmitField("Search Movie")

def movieData(movName):
    response = requests.get(MOVIE_ENDPOINT, params={"api_key": API_KEY, "query": movName})
    data = response.json()["results"]
    return data
#CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-collection.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year= db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(400), nullable=True)
    img_url = db.Column(db.String(1000), nullable=True)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'

db.create_all()


new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
# db.session.add(new_movie)
# db.session.commit()
# ordered_movies = Movie.query.order_by(Movie.rating.desc()).all()
# i = 1
# for movie in ordered_movies:
#     movie.ranking = i
#     i += 1
# db.session.commit()

@app.route("/")
def home():

    # all_movie = db.session.query(Movie).all()
    # print(all_movie)
    db_data = Movie.query.order_by('rating').all()
    for i in range(len(db_data)):
        db_data[i].ranking = len(db_data) - i
        db.session.commit()

    #This logic is for arranging movie in descending order Start from Rank 1 movie
    # db_data=Movie.query.order_by(Movie.rating.desc()).all()
    # i = 1
    # for movie in db_data:
    #     movie.ranking = i
    #     i += 1
    #     db.session.commit()

    return render_template("index.html",data=db_data)



@app.route("/select",methods=["POST","GET"])
def select():
    movie_id=request.args.get("id")
    movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_id}"
    response = requests.get(movie_api_url, params={"api_key": API_KEY})
    data = response.json()
    if data['poster_path'] != None:
        img_url=MOVIE_IMAGE_URL + data['poster_path']
    else:
        img_url=None

    new_movie = Movie(
        title=data['original_title'],
        year=data['release_date'][0:4],
        description=data['overview'],
        rating=None,
        ranking=None,
        review=None,
        img_url=img_url
    )
    db.session.add(new_movie)
    db.session.commit()
    mov_data = Movie.query.filter_by(title=data['original_title']).first()
    return redirect(f"/update/{mov_data.id}")


@app.route("/add",methods=["POST","GET"])
def add():
    form = AddMovieForm()
    if request.method == "POST":
        return render_template("select.html",data=movieData(form.movie.data))
    return render_template("add.html",form=form)



@app.route("/update/<id>",methods=["POST","GET"])
def update(id):
    form=RateMovieForm()
    if request.method == "POST":
        movie_to_update = Movie.query.filter_by(id=id).first()
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect("/")

    movie = Movie.query.filter_by(id=id).first()
    return render_template("edit.html",form=form, data=movie)



@app.route('/delete/<id>',methods=["GET","POST"])
def delete(id):

    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
