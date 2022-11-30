from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, NumberRange
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-movie-collections.db'
db = SQLAlchemy(app)
KEY = 'f1d19547e02aaac1a269fdefefc27d96'


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(300))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(150))
    img_url = db.Column(db.String(1000), nullable=False)

class EditForm(FlaskForm):
    rating = FloatField(label='Ваша оцінка до 10 наприклад 7.5', validators=[DataRequired()])
    review = StringField(label='Ваші враження', validators=[DataRequired()])
    submit = SubmitField('Підтвердити')

class AddMovie(FlaskForm):
    title = StringField(label='Назва фільму', validators=[DataRequired()])
    submit = SubmitField('Добавити')

@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()
    for movie in range(len(movies)):
        movies[movie].ranking = len(movies)-movie
        db.session.commit()
    return render_template("index.html", data=movies)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    id = request.args.get('id')
    movie = Movie.query.get(id)
    form = EditForm()
    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect('/')
    return render_template('edit.html', form=form, movie=movie)

@app.route('/delete')
def delete():
    id = request.args.get('id')
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect('/')


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        movies = requests.get(url='https://api.themoviedb.org/3/search/movie',
                              params={'api_key': KEY, "page": 1, 'query': form.title.data})
        return render_template('select.html', movies=movies.json()['results'])
    return render_template('add.html', form=form)

@app.route('/add_data')
def add_data():
    move_id = request.args.get('id')
    data = requests.get(url=f'https://api.themoviedb.org/3/movie/{move_id}', params={'api_key': KEY}).json()
    new_movie = Movie(
        title=data['original_title'],
        year=data['release_date'][:4],
        img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
        description=data['overview']
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
