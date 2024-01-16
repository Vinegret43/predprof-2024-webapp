#!/usr/bin/python3

from flask import Flask, render_template, request

app = Flask(__name__)

@app.get("/")
def root():
    return render_template("user.html")

BOARDS = [
    {
        "name": "Поле 3x3",
        "size": 3,
        "id": 1337,
    },
    {
        "name": "Поле 2x2",
        "size": 2,
        "id": 228,
    },
]

@app.get("/boards")
def boards():
    return BOARDS

@app.get("/board")
def board():
    try:
        board_id = int(request.args.get("id"))
    except Exception as e:
        return f"Invalid parameters: {e}", 400

    if board_id == 1337:
        return [
            "unknown", "unknown", "empty",
            "empty", "unknown", "unknown",
            "/static/prize.png", "unknown", "unknown"
        ]
    elif board_id == 228:
        return [
            "unknown", "/static/prize.png",
            "empty", "unknown",
        ]
    return f"Invalid ID: {id}", 400

# Example: `POST /shoot?x=1&y=1&id=228`
@app.post("/shoot")
def shoot():
    try:
        x = int(request.args.get("x"))
        y = int(request.args.get("y"))
        id = int(request.args.get("id"))
    except Exception as e:
        return f"Invalid parameters: {e}", 400
    if id == 1337:
        try:
            assert 0 <= x <= 2
            assert 0 <= y <= 2
        except Exception as e:
            return f"X or Y out of bounds: {e}", 400
        return {
            "name": "19 dollar fortnite card",
            "image": "prize.png",
            "description": "19 dollar fartnite card. ho wants it?"
        }
    elif id == 228:
        try:
            assert 0 <= x <= 1
            assert 0 <= y <= 1
        except Exception as e:
            return f"X or Y out of bounds: {e}", 400
        return {
            "name": "19 dollar fortnite card",
            "image": "prize.png",
            "description": "19 dollar fartnite card. ho wants it?"
        }
    return f"Invalid ID: {id}", 400

app.run()
