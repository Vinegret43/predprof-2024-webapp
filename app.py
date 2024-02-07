#!/usr/bin/python3


from flask import Flask, jsonify, redirect, url_for, session, render_template, request, send_from_directory
from sqlite3 import connect
import json
from uuid import uuid4
import os

if not os.path.exists("images"):
    os.mkdir("images")

def red(s):
    print(f"\033[31m{s}\033[0m")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "images"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = "S2;lJ^}S8F3[..xf{a}Ju%9%DpSK#iaAXRW;c(J{Neb!lTy^oZoB1tyz!.yF,HD"

connection = connect('Users2.sqlite', check_same_thread=False)

@app.get('/')
def main(error_message=None):
    if 'username' in session:
        username = session["username"]
        if user_is_admin(username):
            return render_template('admin.html')
        else:
            return render_template('user.html')
    return render_template('login.html', error_message=error_message)

@app.get("/prizes")
def prizes_view():
    username = session["username"]
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT prizes FROM allUsers WHERE login = ?", (username,))
        prize_ids = json.loads(cursor.fetchone()[0])
        prizes = {}
        for id in prize_ids:
            prize = cursor.execute("SELECT * FROM gifts WHERE id = ?", (id,)).fetchone()
            id, name, image, description, _ = prize
            if id in prizes:
                prizes[id]["amount"] += 1
            else:
                prizes[id] = {
                    "name": name,
                    "image": image,
                    "description": description,
                    "amount": 1,
                }
    return render_template("prizes.html", prizes=prizes)

@app.post('/api/login')
def login():
    username = request.form["username"]
    password = request.form["password"]

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM allUsers WHERE login = ?", (username,))
        data = cursor.fetchone()
    if data is None:
        return main("Неверное имя пользователя или пароль")
    elif data[0] == password:
        session['username'] = username
        return redirect(url_for('main'))
    else:
        return main("Неверное имя пользователя или пароль")


@app.post('/api/register')
def register():
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT max(rowid) FROM allUsers")
        id = cursor.fetchall()[0][0]
    if id is None:
        id = 0
    username = request.form["username"]
    password = request.form["password"]
    if request.form.get("is_admin"):
        is_admin = str(bool(request.form["is_admin"]))
    else:
        is_admin = False

    if not username.strip() or not password.strip():
        return main("Недопустимое имя пользователя или пароль")

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT count(*) FROM allUsers WHERE login = ?", (username,))
        data = cursor.fetchone()
    if data[0] != 0:
        return main("Имя пользователя занято")
    else:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO allUsers (id, login, password, admin) 
                VALUES  (?, ?, ?, ?)""",
                (id, username, password, is_admin),
            )
        connection.commit()

        session["username"] = username
        return redirect(url_for("main"))


@app.get('/api/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))


@app.get('/api/boards')
def boards():
    username = session["username"]
    boards = list()
    if user_is_admin(username):
        with connection:
            cursor = connection.cursor()
            boards_query = cursor.execute("SELECT * FROM fields").fetchall()

        with connection:
            cursor = connection.cursor()
            users_query = cursor.execute("SELECT login, fields FROM allUsers WHERE admin != 'True'").fetchall()
        users = map(lambda entry: (entry[0], json.loads(entry[1])), users_query)

        boards = {}
        for i in boards_query:
            board = {
                "name": i[3],
                "size": i[1],
                "id": i[0],
                "shotsFiredBy": json.loads(i[4]),
                "users": {},
            }
            boards[i[0]] = board

        for username, user_boards in users:
            for board, shots in user_boards.items():
                boards[int(board)]["users"][username] = shots

        boards = list(boards.values())
    else:
        with connection:
            cursor = connection.cursor()
            fields = cursor.execute(
                "SELECT fields FROM allUsers WHERE login = ?",
                (username,)
            ).fetchall()[0][0]
            fields = json.loads(fields)
        for field_id, shots in fields.items():
            with connection:
                cursor = connection.cursor()
                field_values = cursor.execute("SELECT * FROM fields WHERE id = ?", (field_id,)).fetchone()
            content = json.loads(field_values[2])
            for entry in content:
                if not entry["shot"]:
                    entry["prize"] = None
            field = {
                "name": field_values[3],
                "size": field_values[1],
                "id": field_values[0],
                "shots": shots,
                "content": content,
            }
            boards.append(field)

    return jsonify(boards)


@app.post('/api/createBoard')
def create_board():
    name = request.form["name"]
    size = int(request.form["size"])
    assert 2 <= size <= 30
    with connection:
        cursor = connection.cursor()
        newId = len(cursor.execute("SELECT * FROM fields").fetchall())
    contents = [{"shot": False, "prize": None}] * (size**2)
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO fields (id, Size, dataField, name)  VALUES  (?, ? ,? , ?)",
        (newId, size, json.dumps(contents), name)
        )
    connection.commit()
    return str(newId)


@app.post('/api/deleteBoard')
def delete_board():
    id = int(request.form["id"])
    with connection:
        cursor = connection.cursor()
        shots_fired_by = json.loads(cursor.execute("SELECT shotsFiredBy FROM fields WHERE id = ?", (id,)).fetchone()[0])
        if shots_fired_by:
            return "Нельзя удалить поле", 400
        cursor.execute("DELETE from fields where id = ?", (id,))
        users = cursor.execute("SELECT login, fields FROM allUsers WHERE admin != 'True'").fetchall()
        for username, boards in users:
            boards = json.loads(boards)
            if id in boards:
                del boards[id]
                boards = json.dumps(boards)
                cursor.execute("UPDATE allUsers SET fields = ? WHERE login = ?", (boards, username)).fetchall()

    connection.commit()
    return "", 200

@app.get('/api/prizes')
def prizes():
    prizes = []
    with connection:
        cursor = connection.cursor()
        a = cursor.execute("SELECT * FROM gifts").fetchall()
    for i in a:
        b = {
            "name": i[1],
            "image": i[2],
            "description": i[3],
            "id": i[0],
            "isWon": i[4]
        }
        prizes.append(b)
    return jsonify(prizes)

@app.post('/api/createPrize')
def create_prize():
    file = request.files["icon"]
    filename = str(uuid4())
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    image_url = f"/images/{filename}"
    name = request.form["name"]
    description = request.form["description"]
    with connection:
        cursor = connection.cursor()
        a = cursor.execute("SELECT * FROM gifts").fetchall()
    id = len(a)
    isWon = "False"
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO gifts (id, name, image, description, isWon)  VALUES  (?, ?, ?, ?, ?)",
            (id, name, image_url, description, isWon)
        )
    connection.commit()
    prize = {
        "name": name,
        "description": description,
        "image": image_url,
        "id": id,
        "isWon": isWon,
    }
    return jsonify(prize)


@app.post('/api/editPrize')
def edit_prize():
    idN = int(request.form["id"])
    if "name" in request.form:
        new_name = request.form["name"]
        with connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE gifts SET name = ? WHERE id = ?", (new_name, idN)).fetchall()
        connection.commit()
    if "description" in request.form:
        new_description = request.form["description"]
        with connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE gifts SET description = ? WHERE id = ?", (new_description, idN)).fetchall()
        connection.commit()
    if request.files.get("icon"):
        file = request.files["icon"]
        filename = str(uuid4())
        image_url = f"/images/{filename}"
        with connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE gifts SET image = ? WHERE id = ?", (image_url, idN)).fetchall()
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return "", 200


@app.post('/api/deletePrize')
def delete_prize():
    id = int(request.form["id"])
    with connection:
        cursor = connection.cursor()
        is_won = cursor.execute("SELECT isWon FROM gifts WHERE id = ?", (id,)).fetchone()[0]
        if is_won == "True":
            return "Приз нельзя удалить", 400
        cursor.execute("DELETE from gifts where id = ?", (id,))
    connection.commit()
    return "", 200

@app.post('/api/putPrize')
def put_prize():
    board_id = int(request.form["board_id"])
    prize_id = int(request.form["prize_id"])
    x = int(request.form["x"])
    y = int(request.form["y"])
    with connection:
        cursor = connection.cursor()
        assert cursor.execute("SELECT * FROM gifts WHERE id = ?", (prize_id,)).fetchone()
        cursor.execute("UPDATE gifts SET isWon = 'True' WHERE id = ?", (prize_id,)).fetchall()
        board = cursor.execute("SELECT * FROM fields WHERE id = ?", (board_id,)).fetchone()
        if json.loads(board[4]):
            return "Нельзя редактировать это поле", 400
        content = json.loads(board[2])
        size = board[1]
        content[y*size + x]["prize"] = prize_id
        content = json.dumps(content)
        cursor.execute("UPDATE fields SET dataField = ? WHERE id = ?", (content, board_id)).fetchall()
    return "", 200

@app.post('/api/clearPrize')
def clear_prize():
    board_id = int(request.form["board_id"])
    x = int(request.form["x"])
    y = int(request.form["y"])
    with connection:
        cursor = connection.cursor()
        board = cursor.execute("SELECT * FROM fields WHERE id = ?", (board_id,)).fetchone()
        if json.loads(board[4]):
            return "Нельзя редактировать это поле", 400
        content = json.loads(board[2])
        size = board[1]
        content[y*size + x]["prize"] = None
        content = json.dumps(content)
        cursor.execute("UPDATE fields SET dataField = ? WHERE id = ?", (content, board_id)).fetchall()
    return "", 200


@app.get('/api/users')
def users():
    users = []
    with connection:
        cursor = connection.cursor()
        a = cursor.execute("SELECT * FROM allUsers").fetchall()
    for i in a:
        if i[3] != "True":
            b = {
                "username": i[1],
                "id": i[0],
            }
            users.append(b)
    return jsonify(users)


@app.post('/api/addPlayer')
def add_player():
    board_id = int(request.form["board_id"])
    username = str(request.form["username"])
    with connection:
        cursor = connection.cursor()
        assert cursor.execute("SELECT * FROM fields WHERE id = ?", (board_id,)).fetchone()
        fields = cursor.execute("SELECT fields FROM allUsers WHERE login = ?", (username,)).fetchone()[0]
        fields = json.loads(fields)
        fields[board_id] = 0
        fields = json.dumps(fields)
        cursor.execute("UPDATE allUsers SET fields = ? WHERE login = ?", (fields, username))
    return "", 200


@app.post('/api/removePlayer')
def remove_player():
    board_id = request.form["board_id"]
    username = str(request.form["username"])
    with connection:
        cursor = connection.cursor()
        shots_fired_by = cursor.execute("SELECT shotsFiredBy FROM fields WHERE id = ?", (board_id,)).fetchone()[0]
        if username in json.loads(shots_fired_by):
            return "Нельзя удалить игрока", 400
        fields = cursor.execute("SELECT fields FROM allUsers WHERE login = ?", (username,)).fetchone()[0]
        fields = json.loads(fields)
        del fields[board_id]
        fields = json.dumps(fields)
        cursor.execute("UPDATE allUsers SET fields = ? WHERE login = ?", (fields, username))
    return "", 200


@app.post('/api/setNumberOfShots')
def set_number_of_shots():
    username = request.form["username"]
    board_id = request.form["board_id"]
    shots = int(request.form["shots"])
    with connection:
        cursor = connection.cursor()
        assert cursor.execute("SELECT * FROM fields WHERE id = ?", (board_id,)).fetchone()
        fields = cursor.execute("SELECT fields FROM allUsers WHERE login = ?", (username,)).fetchone()[0]
        fields = json.loads(fields)
        fields[board_id] = shots
        fields = json.dumps(fields)
        cursor.execute("UPDATE allUsers SET fields = ? WHERE login = ?", (fields, username))
    return "", 200


@app.get('/api/board')
def board():
    id = int(request.args["id"])
    username = session["username"]

    if user_is_admin(username):
        with connection:
            cursor = connection.cursor()
            board_content = cursor.execute("SELECT dataField FROM fields WHERE id = ?", (id,)).fetchone()[0]
    else:
        with connection:
            cursor = connection.cursor()
            board_content = cursor.execute("SELECT dataField FROM fields WHERE id = ?", (id,)).fetchone()[0]
        board_content = list(map(
            lambda entry: {"shot": False, "prize": None} if not entry["shot"] else entry,
            json.loads(board_content),
        ))

    return board_content


@app.post('/api/shoot')
def shoot():
    board_id = int(request.form["board_id"])
    x = int(request.form["x"])
    y = int(request.form["y"])
    username = session["username"]

    with connection:
        cursor = connection.cursor()
        # Verifying and decrimenting number of shots
        shots = json.loads(cursor.execute("SELECT fields FROM allUsers WHERE login = ?", (username,)).fetchone()[0])
        assert shots[str(board_id)] > 0
        shots[str(board_id)] -= 1
        cursor.execute("UPDATE allUsers SET fields = ? WHERE login = ?", (json.dumps(shots), username)).fetchall()

        # Updating contents, setting "shot" property to true
        content, size = cursor.execute("SELECT dataField, size FROM fields WHERE id = ?", (board_id,)).fetchone()
        content = json.loads(content)
        prize_id = content[y*size + x]["prize"]
        content[y*size + x]["shot"] = True
        content = json.dumps(content)
        cursor.execute("UPDATE fields SET dataField = ? WHERE id = ?", (content, board_id)).fetchall()

        # Updating shotsFiredBy
        shots_fired_by = cursor.execute("SELECT shotsFiredBy FROM fields WHERE id = ?", (board_id,)).fetchone()[0]
        shots_fired_by = json.loads(shots_fired_by)
        if username not in shots_fired_by:
            shots_fired_by.append(username)
        shots_fired_by = json.dumps(shots_fired_by)
        cursor.execute("UPDATE fields SET shotsFiredBy = ? WHERE id = ?", (shots_fired_by, board_id,)).fetchall()

        if prize_id != None:
            prizes = json.loads(cursor.execute("SELECT prizes FROM allUsers WHERE login = ?", (username,)).fetchone()[0])
            prizes.append(prize_id)
            prizes = json.dumps(prizes)
            cursor.execute("UPDATE allUsers SET prizes = ? WHERE login = ?", (prizes, username)).fetchone()

    return jsonify(prize_id)


@app.route('/images/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def user_is_admin(username):
    with connection:
        cursor = connection.cursor()
        is_admin = cursor.execute("SELECT admin FROM allUsers where login = ?", (username,)).fetchone()[0]
        if is_admin == "True":
            return True
    return False

if __name__ == '__main__':
    app.run()
