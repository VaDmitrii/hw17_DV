# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
ns_movies = api.namespace('movies')
ns_directors = api.namespace('directors')
ns_genres = api.namespace('genres')

# app.json.ensure_ascii


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MoviesSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


movie_schema = MoviesSchema()
movies_schema = MoviesSchema(many=True)


@ns_movies.route('/')
class MoviesView(Resource):

    def get(self):

        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        movies_query = db.session.query(Movie)
        if director_id:
            movies_query = movies_query.filter(Movie.director_id == director_id)
        if genre_id:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)
        if director_id and genre_id:
            movies_query = movies_query.filter(Movie.director_id == director_id).filter(Movie.genre_id == genre_id)
        return movies_schema.dump(movies_query.all()), 200


@ns_movies.route('/<int:mid>')
class MovieView(Resource):

    def get(self, mid):
        movie = db.session.query(Movie).get(mid)
        return movie_schema.dump(movie), 200

@ns_directors.route('/')
class DirectorsView(Resource):

    def post(self):
        req_object = request.json
        director = Director(**req_object)
        with db.session.begin():
            db.session.add(director)
        return '', 204


@ns_directors.route('/<int:director_id>')
class DirectorView(Resource):

    def put(self, director_id):
        req_json = request.json

        try:
            director = db.session.query(Director).get(director_id)

            director.name = req_json.get("name")

            db.session.add(director)
            db.session.commit()

            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, director_id):
        director = db.session.query(Director).get(director_id)
        db.session.delete(director)
        db.session.commit()

        return '', 204


@ns_genres.route('/')
class GenresView(Resource):

    def post(self):
        req_object = request.json
        genre = Genre(**req_object)
        with db.session.begin():
            db.session.add(genre)
        return '', 204


@ns_genres.route('/<int:genre_id>')
class GenreView(Resource):

    def put(self, genre_id):
        req_json = request.json

        try:
            genre = db.session.query(Genre).get(genre_id)

            genre.name = req_json.get("name")

            db.session.add(genre)
            db.session.commit()

            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, genre_id):
        genre = db.session.query(Genre).get(genre_id)
        db.session.delete(genre)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
