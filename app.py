from flask import Flask, jsonify, redirect, url_for, session, render_template, request

app = Flask(__name__)
app.secret_key = "S2;lJ^}S8F3[..xf{a}Ju%9%DpSK#iaAXRW;c(J{Neb!lTy^oZoB1tyz!.yF,HD"

@app.get('/')
def main(error_message=None):
    if 'username' in session:
        is_admin = 0 # TODO: Запросить из БД
        if is_admin:
            return render_template('admin.html')
        else:
            return render_template('user.html')
    return render_template('login.html', error_message=error_message)

@app.post('/api/login')
def login():
    username = request.form["username"]
    password = request.form["password"]
    valid_user = False # TODO: Подтвердить пароль пользователя в БД
    if valid_user:
        session['username'] = username
        return redirect(url_for('main'))
    else:
        return main("Неверное имя пользователя или пароль")

@app.post('/api/register')
def register():
    username = request.form["username"]
    password = request.form["password"]
    is_admin = bool(request.form["is_admin"])
    
    if not username.strip() or not password.strip():
        return main("Недопустимое имя пользователя или пароль")

    user_exists = False # TODO: попробовать записать пользователя в БД. Если пользователь
    # уже существует, записать в эту переменную True

    if user_exists:
        return main("Имя пользователя занято")
    else:
        session["username"] = username
        return redirect(url_for("main"))

@app.get('/api/logout') 
def logout(): 
    session.clear()
    return redirect(url_for('main'))

@app.get('/api/boards')
def boards():
    username = session["username"]
    is_admin = False # TODO: Запросить у бд, является ли пользователь админом
    if is_admin:
        boards = [] # TODO: Запросить все существующие таблицы
    else:
        boards = [] # TODO: Запросить все таблицы, доступные данному юзеру
    return jsonify(boards)

@app.post('/api/createBoard')
def create_board():
    name = request.form["name"]
    size = int(request.form["size"])
    assert size > 2
    board_id = 1337 # TODO: Создать новую таблицу в БД, вернуть её ID
    return str(board_id)

@app.post('/api/deleteBoard')
def delete_board():
    id = int(request.form("id"))
    # TODO: Запрос в БД удаление поля по id

@app.get('/api/prizes')
def prizes():
    is_admin = False # TODO: Запросить у БД, является ли пользователь админом 
    if is_admin:
        prizes = [] # TODO: Запрос из БД списка словарей формата {'name': str, 'image': str, 'description': str, 'id': int, 'isWon': bool}
        return jsonify(prizes)
    else:
        return render_template("prizes.html")

@app.post('/api/createPrize')
def create_prize():
    name = request.form["name"]
    description = request.form["description"]
    # TODO: принимать файл с иконкой
    id = 1337 # TODO: создать приз в БД, вернуть ID
    return str(id)

@app.post('/api/editPrize')
def edit_prize():
    id = int(request.form["id"])
    if "name" in request.form:
        new_name = request.form["name"]
        # TODO: Обновить имя в БД
    if "description" in request.form:
        new_description = request.form["description"]
        # TODO: Обновить описание в БД
    # TODO: обновление иконки

@app.post('/api/deletePrize')
def delete_prize():
    id = int(request.form["id"])
    # TODO: Запрос в БД на удаление приза по id

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
    users = [] # TODO: Запрос из БД списка словарей формата {'username': str, 'user_id': int}
    return jsonify(users)

@app.post('/api/addPlayer')
def add_player():
    board_id = int(request.form("board_id"))
    user_id = int(request.form("user_id"))
    # TODO: Дать игроку доступ к полю в БД

@app.post('/api/setNumberOfShots')
def set_number_of_shots():
    user_id = int(request.form["user_id"])
    board_id = int(request.form["board_id"])
    shots = int(request.form["shots"])
    # TODO: Запись в БД в таблицу полей по (board_id) {user_id:shots} в user_shots_dict

@app.get('/api/board') 
def board():
    id = int(request.args["id"])
    board_content = [] # TODO: Возвратить информацию о каждой клетке поля в формате списка.
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
    field_info = None # TODO: Запросить из БД информацию о данной клетке.
    # Возвращает либо None, либо словарь с информацией о выигранном призе следующего
    # формата: {"name": str, "image": str, "description": str}
    return jsonify(field_info)

if __name__ == '__main__':
    app.run()
