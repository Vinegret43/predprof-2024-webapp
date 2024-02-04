const HOST = "http://" + window.location.host;

var prizes = [];
var boards = [];

function createBoard(title, shots, size, content, id) {
  // Taking a pre-made template and just modifying it
  let board_element = document.querySelector(".board").cloneNode(true);

  board_element.querySelector(".board_title").innerText = title;
  board_element.querySelector(".board_shots").innerText = shots;
  board_element.board_id = id;

  const grid = board_element.querySelector(".grid");
  grid.style.setProperty("--grid-columns", size);

  content.forEach(entry => {
    const element = document.createElement("div");

    if (entry["prize"] != null) {
      let image = document.createElement("img");
      image.src = getById(prizes, entry["prize"]).image;
      element.appendChild(image);
    }

    if (entry["shot"]) {
      element.classList.add("hitCell");
    }

    element.addEventListener("click", handleCellClick);
    grid.appendChild(element);
  });

  return board_element;
}

function buildBoards(boards) {
  const list = document.querySelector(".boards_list");
  list.innerText = "";
  boards.forEach(board => {
    const { name, size, id, shots, content } = board;
    const board_element = createBoard(name, shots, size, content, id);
    list.appendChild(board_element);
  });
}

// Функция для отправки запроса на сервер при клике на клетку
function handleCellClick(event) {
  const cell = event.target;
  const boardId = cell.closest('.board').board_id;
  const cellIndex = Array.from(cell.parentNode.children).indexOf(cell);
  const board = getById(boards, boardId);
  if (board.shots == 0) {
    return;
  } else {
    board.shots -= 1;
  }
  if (Array.from(cell.classList).includes("hitCell")) {
    return;
  }

  // Отправка запроса на сервер
  let form_data = new FormData();
  form_data.append("board_id", boardId);
  form_data.append("x", cellIndex % board.size);
  form_data.append("y", Math.floor(cellIndex / board.size));
  fetch(HOST + '/api/shoot', {
    method: 'POST',
    body: form_data,
  })
  .then(response => response.json())
  .then(result => {
    // Обновление клетки в зависимости от результата
    board.content[cellIndex].shot = true;
    board.content[cellIndex].prize = result;
    buildBoards(boards);
    if (result != null) {
      window.alert("Поздравляем! Вы выиграли приз!");
    } else {
      window.alert("Увы, в данной клетке не оказалось приза :(");
    }
  })
  .catch(error => {
    console.error('Ошибка при отправке запроса:', error);
  });
}

async function fetchBoards() {
  const response = await fetch(HOST + "/api/boards");
  const boards = await response.json();
  return boards;
}

async function fetchPrizes() {
  const response = await fetch(HOST + "/api/prizes");
  const prizes = await response.json();

  return prizes;
}

function getById(array, id) {
  return array.filter(item => item.id == id)[0];
}

fetchPrizes().then(
  fetched_prizes => {
    prizes = fetched_prizes;
    fetchBoards().then(
      fetched_boards => {
        boards = fetched_boards;
        buildBoards(boards);
      }
    );
  }
);

