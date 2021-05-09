from . import db
from flask_login import UserMixin

favorite = db.Table('favorite',
                db.Column('userId',db.Integer, db.ForeignKey('user.id'), primary_key = True),
                db.Column('gameID',db.Integer, db.ForeignKey('game.id'), primary_key = True)
                )

player = db.Table('player',
    db.Column('playerID',db.Integer, db.ForeignKey('user.id'), primary_key = True),
    db.Column('gameId',db.Integer, db.ForeignKey('game.id'), primary_key = True),
    db.Column('max_score',db.Integer),
    db.Column('ratting_point', db.Integer)
)
class Comment(db.Model):
    gameID = db.Column(db.Integer, db.ForeignKey('game.id'))
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    added_date = db.Column(db.DateTime)
    commentContent = db.Column(db.String(100))
    id = db.Column(db.Integer, primary_key=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    userName = db.Column(db.String(150), unique=True)
    dateOfBirth = db.Column(db.Date)
    country = db.Column(db.String(100))
    bio = db.Column(db.String(100))
    link = db.Column(db.String(100000))
    sex = db.Column(db.String(15))  # giới tính là nam, nữ, không muốn nói
    gameComment = db.relationship(Comment)
    favoriteList = db.relationship('Game', secondary = favorite)
    gameScore = db.relationship('Game', secondary = player)
    avatar = db.Column(db.Integer, db.ForeignKey('img.id'))

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gameName = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    gamePath = db.Column(db.String(2000), unique=True)
    tag = db.Column(db.String(100))
    gameImgPath = db.Column(db.String(1000))
    gameComment = db.relationship(Comment)
    rankingScore = db.relationship('User', secondary = player)
    # introVideo = db.Column()
    pictureID = db.Column(db.Integer, db.ForeignKey('img.id'))

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

