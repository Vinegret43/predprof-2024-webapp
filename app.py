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
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT admin FROM allUsers WHERE login = ?", (username,))
            is_admin = cursor.fetchone()[0]
        if is_admin == "True":
            return render_template('admin.html')
        else:
            return render_template('user.html')
    return render_template('login.html', error_message=error_message)

@app.get("/prizes")
def prizes_view():
    username = session["username"]
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT prizes from allUsers WHERE login = ?", (username,))
        prize_ids = cursor.fetchone()[0]
        prizes = []
        for id in prize_ids:
            prize = cursor.execute("SELECT * FROM gifts WHERE id = ?", (id,)).fetchone()[0]
            prizes.append({
                "id": prize[0],
                "name": prize[1],
                "image": prize[2],
                "description": prize[3],
            })
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
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT admin FROM allUsers WHERE login = ?", (username,))
    is_admin = cursor.fetchone()[0]
    boards = list()
    if is_admin == 'True':
        with connection:
            cursor = connection.cursor()
            a = cursor.execute("SELECT * FROM fields").fetchall()
        # TODO: Add a "users" field containing all the users who have access to this board
        for i in a:
            b = {
                "name": i[3],
                "size": i[1],
                "id": i[0]
            }
            boards.append(b)
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
                field_values = cursor.execute("SELECT * FROM fields WHERE id = ?", (field_id,)).fetchone()[0]
            field = {
                "name": field_values[3],
                "size": field_values[1],
                "id": field_values[0],
                "shots": shots,
            }
            boards.append(field)

    return jsonify(boards)


@app.post('/api/createBoard')
def create_board():
    name = request.form["name"]
    size = int(request.form["size"])
    assert size >= 2
    with connection:
        cursor = connection.cursor()
        newId = len(cursor.execute("SELECT * FROM fields").fetchall())
    contents = ["unknown"] * (size**2)
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
        cursor.execute("DELETE from fields where id = ?", (id,))
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
            return "Приз уже был выигран, его нельзя удалить", 400
        cursor.execute("DELETE from gifts where id = ?", (id,))
    connection.commit()
    return "", 200

@app.post('/api/putPrize')
def put_prize():
    board_id = int(request.form("board_id"))
    prize_id = int(request.form("prize_id"))
    x = int(request.form("x"))
    y = int(request.form("y"))
    with connection:
        cursor = connection.cursor()
        board = cursor.execute("SELECT * FROM fields WHERE id = ?", (board_id,)).fetchone()[0]
    # TODO: Finish this function


@app.post('/api/clearPrize')
def clear_prize():
    board_id = int(request.form("board_id"))
    x = int(request.form("x"))
    y = int(request.form("y"))
    # TODO: Удалить приз из клетки поля


@app.get('/api/users')
def users():
    users = []
    with connection:
        cursor = connection.cursor()
        a = cursor.execute("SELECT * FROM allUsers").fetchall()
    red(a)
    for i in a:
        if i[3] == "False":
            b = {
                "username": i[1],
                "id": i[0],
                "fields": i[5],
            }
            users.append(b)
    return jsonify(users)


@app.post('/api/addPlayer')
def add_player():
    board_id = int(request.form["board_id"])
    username = str(request.form["username"])
    # TODO: Дать игроку доступ к полю в БД


@app.post('/api/setNumberOfShots')
def set_number_of_shots():
    username = str(request.form["username"])
    board_id = int(request.form["board_id"])
    shots = int(request.form["shots"])
    # TODO: Запись в БД в таблицу полей по (board_id) {username:shots} в user_shots_dict


@app.get('/api/board')
def board():
    id = int(request.args["id"])
    board_content = []  # TODO: Возвратить информацию о каждой клетке поля в формате списка.
    # Значения идут построчно: сначала значения первой строки слева направо, затем второй и
    # и так далее. Информация о каждой клетке закодирована в формате строки. Возможны
    # следующие значения:
    # - "unknown" - Никто ещё не стрелял в эту клетку. Неизвестно, что там
    # - "empty" - В клетку уже стреляли и она оказалась пустой
    # - "/path/to/icon.png" - Здесь есть приз, его уже выиграли. Строка содержит путь
    #  до иконки приза

    return jsonify(board_content)


@app.post('/api/shoot')
def shoot():
    board_id = int(request.form["board_id"])
    x = int(request.form["x"])
    y = int(request.form["y"])
    field_info = None  # TODO: Запросить из БД информацию о данной клетке.
    # Возвращает либо null, либо словарь с информацией о выигранном призе следующего
    # формата: {"name": str, "image": str, "description": str, "id": int}
    return jsonify(field_info)


@app.route('/images/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run()
