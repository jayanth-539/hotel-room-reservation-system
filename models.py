from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.Integer, unique=True)
    floor = db.Column(db.Integer)
    position = db.Column(db.Integer)
    occupied = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "room_no": self.room_no,
            "floor": self.floor,
            "position": self.position,
            "occupied": self.occupied
        }
