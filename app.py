from flask import Flask, jsonify, redirect, url_for, session, render_template, request
from sqlite3 import connect

app = Flask(__name__)
app.secret_key = "S2;lJ^}S8F3[..xf{a}Ju%9%DpSK#iaAXRW;c(J{Neb!lTy^oZoB1tyz!.yF,HD"

connection = connect('Users2.sqlite')
cursor = connection.cursor()


@app.get('/')
def main(error_message=None):
    if 'username' in session:
        username = session["username"]
        cursor.execute(f"SELECT admin FROM allUsers WHERE login = ?", (username,))
        is_admin = cursor.fetchone()[0]
        if is_admin == 'true':
            return render_template('admin.html')
        else:
            return render_template('user.html')
    return render_template('login.html', error_message=error_message)


@app.post('/api/login')
def login():
    username = request.form["username"]
    password = request.form["password"]

    cursor.execute(f"SELECT password FROM allUsers WHERE login = ?", (username,))
    data = cursor.fetchone()
    if data is None:
        return main("Неверное имя пользователя")
    elif data[0] == password:
        session['username'] = username
        return redirect(url_for('main'))
    else:
        return main("Неверный пароль")


@app.post('/api/register')
def register():
    cursor.execute("SELECT max(rowid) FROM allUsers")
    id = cursor.fetchall()[0][0]
    username = request.form["username"]
    password = request.form["password"]
    is_admin = str(bool(request.form["is_admin"]))

    if not username.strip() or not password.strip():
        return main("Недопустимое имя пользователя или пароль")

    cursor.execute("SELECT count(*) FROM allUsers WHERE login = ?", (username,))
    data = cursor.fetchone()
    if data == 1:
        return main("Имя пользователя занято")
    else:
        sqlite_insert_query = f"""INSERT INTO allUsers (id, login, password, admin)  VALUES  ({id}, '{username}', '{password}', '{is_admin}')"""
        cursor.execute(sqlite_insert_query)
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
    cursor.execute(f"SELECT admin FROM allUsers WHERE login = ?", (username,))
    is_admin = cursor.fetchone()[0]
    if is_admin == 'true':
        boards = list()
        a = cursor.execute(f"SELECT * FROM fields").fetchall()
        for i in a:
            b = {
                "name": i[3],
                "size": i[1],
                "id": i[0]
            }
            boards.append(b)
    else:
        boards = list()
        fieldIdByLogin = cursor.execute(f"SELECT field_id FROM allUsers WHERE login = ?", (username,)).fetchall()
        q = fieldIdByLogin.split("|")
        for i in q:
            v = cursor.execute(f"SELECT * FROM fields WHERE id = ?", (int(i),)).fetchall()
            for j in v:
                b = {
                    "name": j[3],
                    "size": j[1],
                    "id": j[0]
                }
                boards.append(b)

    return jsonify(boards)


@app.post('/api/createBoard')
def create_board():
    name = request.form["name"]
    size = int(request.form["size"])
    assert size > 2
    newId = len(cursor.execute(f"SELECT * FROM fields").fetchall())
    g = ""
    for i in range(size):
        g += "0|" * size
        g += "/"
    newBoard = f"""INSERT INTO fields (id, Size, dataField, name)  VALUES  ({newId}, '{size}', '{g[:-2]}', '{name}')"""
    cursor.execute(newBoard)
    connection.commit()
    board_id = newId
    return str(board_id)


@app.post('/api/deleteBoard')
def delete_board():
    id = int(request.form("id"))
    cursor.execute("DELETE from fields where id = ?", (id,))
    connection.commit()


@app.get('/api/prizes')
def prizes():
    username = session["username"]
    cursor.execute(f"SELECT admin FROM allUsers WHERE login = ?", (username,))
    is_admin = cursor.fetchone()[0]
    if is_admin == 'true':
        prizes = []
        a = cursor.execute(f"SELECT * FROM gifts").fetchall()
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
    else:
        return render_template("prizes.html")


@app.post('/api/createPrize')
def create_prize():
    # TODO: принимать файл с иконкой
    data = "/images/<WHATEVER>"
    name = request.form["name"]
    description = request.form["description"]
    a = cursor.execute(f"SELECT * FROM gifts").fetchall()
    id = len(a)
    isWon = "False"
    newGift = f"""INSERT INTO gifts (id, name, image, description, isWon)  VALUES  ({id}, '{name}', '{data}', '{description}, '{isWon}')"""
    cursor.execute(newGift)
    connection.commit()
    return str(id)


@app.post('/api/editPrize')
def edit_prize():
    idN = int(request.form["id"])
    if "name" in request.form:
        new_name = request.form["name"]
        cursor.execute("""UPDATE allUsers SET name = ? WHERE id = ? """, (new_name, idN)).fetchall()
        connection.commit()
    if "description" in request.form:
        new_description = request.form["description"]
        cursor.execute("""UPDATE allUsers SET description = ? WHERE id = ? """, (new_description, idN)).fetchall()
        connection.commit()
    # TODO: обновление иконки


@app.post('/api/deletePrize')
def delete_prize():
    id = int(request.form["id"])
    cursor.execute("DELETE from gifts where id = ?", (id,))
    connection.commit()


@app.post('/api/putPrize')
def put_prize():
    board_id = int(request.form("board_id"))
    prize_id = int(request.form("prize_id"))
    x = int(request.form("x"))
    y = int(request.form("y"))
    # TODO: Добавить приз в клетку поля


@app.post('/api/clearPrize')
def clear_prize():
    board_id = int(request.form("board_id"))
    x = int(request.form("x"))
    y = int(request.form("y"))
    # TODO: Удалить приз из клетки поля


@app.get('/api/users')
def users():
    users = []
    a = cursor.execute(f"SELECT * FROM allUsers").fetchall()
    for i in a:
        if i[3] == "False":
            b = {
                "username": i[1],
                "id": i[0]
            }
            users.append(b)
    return jsonify(users)


@app.post('/api/addPlayer')
def add_player():
    board_id = int(request.form("board_id"))
    username = str(request.form("username"))
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
    # Возвращает либо None, либо словарь с информацией о выигранном призе следующего
    # формата: {"name": str, "image": str, "description": str}
    return jsonify(field_info)


if __name__ == '__main__':
    app.run()
