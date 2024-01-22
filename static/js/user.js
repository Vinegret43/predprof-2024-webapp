function createBoard(title, shots, size, content) {
    // Taking a pre-made template and just modifying it
    let element = document.getElementsByClassName("board")[0].cloneNode(true);

    element.getElementsByClassName("board_title")[0].innerHTML = title;
    element.getElementsByClassName("board_shots")[0].innerHTML = "Количество выстрелов: " + shots;

    let table = element.getElementsByTagName("table")[0];

    for (let y = 0; y < size; y++) {
        console.log(document.createElement);
        let row = document.createElement("tr");
        for (let x = 0; x < size; x++) {
            let entry = document.createElement("td");
            if (content[y * size + x] == "unknown") {
               entry.innerHTML = "[]";
               entry.addEventListener("click", function() {
          fetch('https://example.com/api/shoot', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ boardId: title, cellIndex: y * size + x }),
          })
          .then(response => response.json())
          .then(result => {
            if (result === 'hit') {
              entry.innerHTML = "H"; // Обновляем клетку в зависимости от результата
            } else if (result === 'miss') {
              entry.innerHTML = "M"; // Обновляем клетку в зависимости от результата
            }
            // TODO: Добавить обработку других возможных результатов
          })
          .catch(error => {
            console.error('Ошибка при отправке запроса:', error);
          });
        });
            } else if (content[y * size + x] == "empty") {
               entry.innerHTML = "X";
            } else {
                entry.innerHTML = "P";
            }
            row.appendChild(entry);
        }
        table.appendChild(row);
    }

    return element;
}

// This code is just for reference: delete it
let content = [
    "unknown", "unknown", "empty",
    "empty", "unknown", "unknown",
    "prize.png", "unknown", "unknown",
];
document.getElementsByClassName("main")[0].appendChild(createBoard("Board title", 12, 3, content));
document.getElementsByClassName("main")[0].appendChild(createBoard("Board title 2", 3, 3, content));

// Функция для запроса данных об игровых полях с сервера
function fetchGameBoards() {
  fetch('https://example.com/api/boards')
    .then(response => response.json())
    .then(data => {
      data.forEach(boardData => {
        const { title, shots, size, content } = boardData;
        const boardElement = createBoard(title, shots, size, content);
        document.getElementsByClassName("main")[0].appendChild(boardElement);
      });
    })
    .catch(error => {
      console.error('Ошибка при получении данных:', error);
    });
}

// Функция для отправки запроса на сервер при клике на клетку
function handleCellClick(event) {
  const cell = event.target;
  const boardId = cell.closest('.board').id;
  const cellIndex = Array.from(cell.parentNode.children).indexOf(cell);

  // Отправка запроса на сервер
  fetch('https://example.com/api/shoot', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ boardId, cellIndex }),
  })
  .then(response => response.json())
  .then(result => {
    // Обновление клетки в зависимости от результата
    if (result === 'hit') {
      cell.classList.add('hitCell');
    } else if (result === 'miss') {
      cell.classList.add('missCell');
    }
  })
  .catch(error => {
    console.error('Ошибка при отправке запроса:', error);
  });
}

// Назначение обработчика клика для всех клеток игровых полей
fetchGameBoards(); // Вызываем функцию для загрузки данных с сервера

// Назначаем обработчик клика для всех клеток игровых полей
document.querySelectorAll('.board td').forEach(cell => {
  cell.addEventListener('click', handleCellClick);
});
