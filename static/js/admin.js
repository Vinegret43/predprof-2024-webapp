var boards = [];
var prizes = [];
const HOST = "http://" + window.location.host;

function displayBoards(boards) {
  const list = document.getElementsByClassName("boards_list")[0];
  list.textContent = "";
  boards.forEach(board => {
    let element = document.getElementsByClassName("boards_list_entry")[0].cloneNode(true);
    list.appendChild(element);
    element.getElementsByClassName("board_title")[0].innerHTML = board.name + "#";
    element.getElementsByClassName("board_id")[0].innerHTML = board.id;
  });
}

async function fetchBoards() {
  const response = await fetch(HOST + "/api/boards");
  const boards = await response.json();
  callbacks = boards.map(board => fetch(HOST + "/api/board?id=" + board.id)
    .then(response => response.json())
    .then(
      contents => {
        board.contents = contents;
      }
    )
  );
  await Promise.all(callbacks);
  return boards;
}

// Filters boards based on the search parameters supplied by the user
function filterBoards(boards) {
  return boards;
}

function displayPrizes(prizes) {
  const list = document.getElementsByClassName("prizes_list")[0];
  list.textContent = "";
  prizes.forEach(prize => {
    let element = document.getElementsByClassName("prizes_list_entry")[0].cloneNode(true);
    list.appendChild(element);
    element.getElementsByClassName("prize_name")[0].innerHTML = prize.name + "#";
    element.getElementsByClassName("prize_id")[0].innerHTML = prize.id;
    element.getElementsByClassName("prize_icon")[0].src = prize.image;
  });
}

async function fetchPrizes() {
  const response = await fetch(HOST + "/api/prizes");
  const prizes = await response.json();

  return prizes;
}

function filterPrizes(prizes) {
  return prizes;
}

function deleteBoard(delete_button) {
  const board_element = delete_button.parentElement;
  const board_id = parseInt(board_element.getElementsByClassName("board_id")[0].innerHTML);
  let form_data = new FormData();
  form_data.append("id", board_id);
  fetch(
    HOST + "/api/deleteBoard",
    {
      method: "POST",
      body: form_data,
    }
  ).then(async response => {
    if (response.ok) {
      boards = boards.filter(board => board.id != board_id);
      displayBoards(filterBoards(boards));
    } else {
      const error_text = await response.text();
      window.alert(error_text)
    }
  });
}

function editBoard(edit_button) {
  const board_element = edit_button.parentElement;
  const board_id = parseInt(board_element.getElementsByClassName("board_id")[0].innerHTML);
  const board = boards.filter(board => board.id == board_id)[0];

  const popup = document.getElementsByClassName("popup_container_hidden")[0];
  popup.hidden = false;
  popup.getElementsByClassName("popup_title")[0].innerHTML = "Редактор полей";
  const board_editor = document.getElementsByClassName("board_editor")[0].cloneNode(true);
  const popup_body = popup.getElementsByClassName("popup_body")[0];
  popup_body.innerText = "";
  popup_body.appendChild(board_editor);
}

function createBoard(form) {
  fetch(HOST + "/api/createBoard",
    {
      method: "POST",
      body: new FormData(form),
    }
  ).then(
    _ => {
      fetchBoards().then(
        fetched_boards => {
          boards = fetched_boards;
          displayBoards(filterBoards(boards));
        }
      );
    }
  );
  form.reset();
  return false;
}

function createPrize(form) {
  fetch(HOST + "/api/createPrize",
    {
      method: "POST",
      body: new FormData(form),
    }
  ).then(
    _ => {
      fetchPrizes().then(
        fetched_prizes => {
          prizes = fetched_prizes;
          displayPrizes(filterPrizes(prizes));
        }
      );
    }
  );
  form.reset();
  return false;
}

function deletePrize(delete_button) {
  const prize_element = delete_button.parentElement;
  const prize_id = parseInt(prize_element.getElementsByClassName("prize_id")[0].innerHTML);
  let form_data = new FormData();
  form_data.append("id", prize_id);
  fetch(
    HOST + "/api/deletePrize",
    {
      method: "POST",
      body: form_data,
    }
  ).then(async response => {
    if (response.ok) {
      prizes = prizes.filter(prize => prize.id != prize_id);
      displayPrizes(filterPrizes(prizes));
    } else {
      const error_text = await response.text();
      window.alert(error_text)
    }
  });
}

function editPrize(edit_button) {
  const prize_element = edit_button.parentElement;
  const prize_id = parseInt(prize_element.getElementsByClassName("prize_id")[0].innerHTML);
  const prize = prizes.filter(prize => prize.id == prize_id)[0];

  const popup = document.getElementsByClassName("popup_container_hidden")[0];
  popup.hidden = false;
  popup.getElementsByClassName("popup_title")[0].innerHTML = "Редактор призов";
  const prize_editor = document.getElementsByClassName("prize_editor")[0].cloneNode(true);
  const popup_body = popup.getElementsByClassName("popup_body")[0];
  popup_body.innerText = "";

  const prize_name = prize_editor.querySelector('input[name="name"]');
  prize_name.value = prize.name;

  const prize_description = prize_editor.getElementsByTagName("textarea")[0];
  prize_description.value = prize.description;

  const prize_id_input = prize_editor.querySelector('input[name="id"]');
  prize_id_input.value = prize.id;

  popup_body.appendChild(prize_editor);
}

function submitPrizeEdit(form) {
  fetch(HOST + "/api/editPrize",
    {
      method: "POST",
      body: new FormData(form),
    }
  ).then(
    _ => {
      fetchPrizes().then(
        fetched_prizes => {
          prizes = fetched_prizes;
          displayPrizes(filterPrizes(prizes));
        }
      );
    }
  );
  form.reset();
  const popup = document.getElementsByClassName("popup_container_hidden")[0];
  popup.hidden = true;
  return false;
}

fetchBoards().then(
  fetched_boards => {
    boards = fetched_boards;
    displayBoards(filterBoards(boards));
  }
);

fetchPrizes().then(
  fetched_prizes => {
    prizes = fetched_prizes;
    displayPrizes(filterPrizes(prizes));
  }
);
