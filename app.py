from flask import Flask, jsonify, redirect, url_for, session


app = Flask(__name__)

@app.route('/api/login?user_name=<str:user_name>&password=<str:password>', methods=['POST'])
def login(user_name, password):
    admin = 0 #Получение из ИЗ роли пользователя, если не находит пользоватя по переданным данным, то = None
    if admin is None:
        return 'null'
    else:
        return jsonify({'admin': admin})


@app.route('/api/register?user_name=<str:user_name>&password=<str:password>&admin=<bool:admin>', methods=['POST'])
def register(user_name, password, admin):
    user_id = 0 #Запрос из БД количество пользователей

    # Запись в БД нового пользователя


@app.route('/api/boards', methods=['GET'])
def boards():
    boards = 0 #Запрос из БД списка словарей ([{'id': int, 'size': int, 'name': str}])

    return jsonify({'boards': boards})


@app.route('/api/createBoard?board_name=<str:board_name>&size=<int:size>', methods=['POST'])
def createBoard(board_name, size):
    id = 0 #Запрос из БД количество полей
    # Запись в БД нового поля 


@app.route('/api/deleteBoard?board_id=<int:board_id>', methods=['POST'])
def deleteBoard(id):
    #Запрос в БД удаление поля по id
    pass


@app.route('/api/prizes', methods=['GET'])
def prizes():
    prizes = 0 #Запрос из БД списка словарей ([{'name': str, 'image': str, 'description': str, 'id': int, 'status': str}]) (Статусы: prize, not_prize, not_shot)

    return jsonify({'prizes': prizes})


@app.route('/api/createPrize?prize_name=<str:prize_name>&description=<str:description>', methods=['POST']) #TODO Сделать приемку файла
def createPrize(prize_name, description):
    id = 0 #Запрос из БД количество призов
    #Запис в БД нового приза


@app.route('/api/editPrize?id=<int:id>&prize_name=<str:prize_name>&description=<str:description>', methods=['POST']) #TODO Сделать приемку файла 
def editPrize(id, prize_name=None, description=None):
    if prize_name is None:
        prize_name = 0 #Запрос name из БД
    if description is None:
        description = 0 #Запрос description из БД

    #Запрос в БД обновление данных о призе
    pass


@app.route('/api/deletePrize?prize_id=<int:prize_id>', methods=['POST'])
def deletePrize(prize_id):
    #Запрос в БД удаление приза по id
    pass


@app.route('/api/putPrize?board_id=<int:board_id>&prize_id=<int:prize_id>&x=<int:x>&y=<int:y>', methods=['POST'])
def putPrize(board_id, prize_id, x, y):
    #Запись в БД в таблицу полей по (board_id) prize_id, x, y
    pass


@app.route('/api/users', methods=['GET']) 
def users():
    users = 0 #Запрос из БД списка словарей ([{'user_name': str, 'user_id': int}])

    return jsonify({'users': users})


@app.route('/api/addPlayer?board_id=<int:board_id>&user_id=<int:user_id>', methods=['POST'])
def addPlayer(board_id, user_id):
    #Запись в БД в таблицу полей по (board_id) user_id в user_id_list
    pass


@app.route('/api/setNumberOfShots?user_id=<int:user_id>&board_id=<int:board_id>&shots=<int:shots>', methods=['POST'])
def setNumberOfShots(user_id, board_id, shots):
    #Запись в БД в таблицу полей по (board_id) {user_id:shots} в user_shots_dict
    pass


@app.route('/api/boardsforuser?user_id=<int:user_id>', methods=['GET']) #TODO В ТЗ другое, надо обсудить
def boardsforuser(user_id):
    boards = [] #Запрос из БД списка словарей ([{'id': int, 'size': int, 'name': str, 'user_id_list': list}])
    for board in boards:
        if user_id not in board['user_id_list']:
            boards.pop(board)

    return jsonify({'boards': boards})


@app.route('/api/board?board_id=<int:board_id>', methods=['GET']) 
def board(board_id):
    board_info = [] #Запрос из БД списка словарей ([{'id': int, 'size': str, 'name': str, 'user_id_list': list, 'fields_list': list}])

    return jsonify({'board_info': board_info})


@app.route('/api/shoot?board_id=<int:board_id>&x=<int:x>&y=<int:y>', methods=['POST']) 
def shoot(board_id, x, y):
    field_info = [] #Запрос из БД списка информации о поле ({'name': str, 'image': str, 'description': str, 'status': str}), если ее нет то None, (Статусы: prize, not_prize, not_shot)
    if field_info is None:
        return 'null'
    else:
        return jsonify({'field_info': field_info})


@app.route('/api/prizes', methods=['GET']) 
def prizes():
    return 'prizes.html'


@app.route('/api/logout', methods=['POST']) 
def logout(): 
    session['logged_in'] = False
    return redirect(url_for('main'))


@app.route('/api/logout', methods=['POST']) 
def logout():
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.run()
