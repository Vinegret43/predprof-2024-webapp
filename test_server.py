#!/usr/bin/python3

from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.get("/")
def root():
    return render_template("admin.html")

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

@app.get("/api/boards")
def boards():
    return BOARDS

DUMMY_PRIZE = {
    "id": 420,
    "name": "19 dollar",
    "description": "fortnite card",
    "image": "/static/images/example_prize.png",
    "isWon": True,
}

@app.get("/api/prizes")
def prizes():
    return [DUMMY_PRIZE, DUMMY_PRIZE]

@app.get("/api/board")
def board():
    try:
        board_id = int(request.args.get("id"))
    except Exception as e:
        return f"Invalid parameters: {e}", 400

    if board_id == 1337:
        return [
            ["unknown", "unknown", "empty"],
            ["empty", "unknown", "unknown"],
            [DUMMY_PRIZE, "unknown", "unknown"]
        ]
    elif board_id == 228:
        return [
            ["unknown", "/static/prize.png"],
            ["empty", "unknown"],
        ]
    return f"Invalid ID: {id}", 400

# Example: `POST /shoot?x=1&y=1&id=228`
@app.post("/api/shoot")
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
        return DUMMY_PRIZE
    elif id == 228:
        try:
            assert 0 <= x <= 1
            assert 0 <= y <= 1
        except Exception as e:
            return f"X or Y out of bounds: {e}", 400
        return DUMMY_PRIZE
    return f"Invalid ID: {id}", 400

@app.post("/api/deleteBoard")
def delete_board():
    id = int(request.form.get("id"))
    if id == 1337:
        return "Ok", 200
    else:
        return "Nah lol, not gonna do it", 400

app.run(debug=True)
