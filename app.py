from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, Room
import itertools
import random

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()
    if Room.query.count() == 0:
        for floor in range(1, 10):
            for pos in range(1, 11):
                db.session.add(Room(
                    room_no=floor * 100 + pos,
                    floor=floor,
                    position=pos
                ))
        for pos in range(1, 8):
            db.session.add(Room(
                room_no=1000 + pos,
                floor=10,
                position=pos
            ))
        db.session.commit()

def horizontal_time(pos):
    return max(pos) - min(pos)

def vertical_time(floors):
    return abs(max(floors) - min(floors)) * 2

def total_travel_time(rooms):
    return vertical_time([r.floor for r in rooms]) + horizontal_time([r.position for r in rooms])

def available_rooms():
    return Room.query.filter_by(occupied=False).all()

def same_floor_booking(count):
    best, best_time = None, float("inf")
    floors = {}
    for r in available_rooms():
        floors.setdefault(r.floor, []).append(r)

    for floor_rooms in floors.values():
        if len(floor_rooms) >= count:
            floor_rooms.sort(key=lambda r: r.position)
            for combo in itertools.combinations(floor_rooms, count):
                t = horizontal_time([r.position for r in combo])
                if t < best_time:
                    best_time, best = t, combo
    return best

def cross_floor_booking(count):
    best, best_time = None, float("inf")
    for combo in itertools.combinations(available_rooms(), count):
        t = total_travel_time(combo)
        if t < best_time:
            best_time, best = t, combo
    return best

@app.route("/rooms")
def rooms():
    return jsonify([r.to_dict() for r in Room.query.order_by(Room.floor, Room.position)])

@app.route("/book", methods=["POST"])
def book():
    count = request.json.get("rooms")
    if not count or count > 5:
        return jsonify({"error": "1–5 rooms allowed"}), 400

    selected = same_floor_booking(count) or cross_floor_booking(count)
    if not selected:
        return jsonify({"error": "No rooms available"}), 400

    for r in selected:
        r.occupied = True
    db.session.commit()

    return jsonify({
        "booked_rooms": [r.room_no for r in selected],
        "travel_time": total_travel_time(selected)
    })

@app.route("/random-occupancy", methods=["POST"])
def random_occupancy():
    for r in Room.query.all():
        r.occupied = random.random() < 0.3
    db.session.commit()
    return jsonify({"message": "Random occupancy generated"})

@app.route("/reset", methods=["POST"])
def reset():
    Room.query.update({Room.occupied: False})
    db.session.commit()
    return jsonify({"message": "Reset complete"})

if __name__ == "__main__":
    app.run()
