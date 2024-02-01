var boards = [];
var prizes = [];
var users = [];
const HOST = "http://" + window.location.host;

var last_board_edited = null;
var board_editor_tool = {
  mode: null, // "delete" or "insert"
  prize: null, // ID of the prize to insert
};

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
  const input = document.querySelector("#boards_search_bar > input");
  return boards.filter(board => board.name.includes(input.value));
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
  const radio_value = document.querySelector('input[name="is_won"]:checked').value;
  if (radio_value == "won") {
    var won_values = ["True"];
  } else if (radio_value == "not_won") {
    var won_values = ["False"];
  } else {
    var won_values = ["True", "False"];
  }
  const input = document.querySelector("#prizes_search_bar > input");
  return prizes.filter(prize => prize.name.includes(input.value) && won_values.includes(prize.isWon));
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
  last_board_edited = board_id;
  const board = getById(boards, board_id);

  const popup = document.getElementsByClassName("popup_container_hidden")[0];
  popup.hidden = false;
  popup.getElementsByClassName("popup_title")[0].innerHTML = "Редактор полей (" + board.name + ")";
  const board_editor = document.getElementsByClassName("board_editor")[0].cloneNode(true);
  const popup_body = popup.getElementsByClassName("popup_body")[0];
  popup_body.innerText = "";
  setupBoardEditor(board_editor, board_id);
  popup_body.appendChild(board_editor);
}

function setupBoardEditor(editor, board_id) {
  const board = getById(boards, board_id);

  // Grid setup
  const grid = editor.querySelector(".grid");
  grid.style.setProperty("--grid-columns", board["size"])
  grid.innerText = "";
  board["contents"].forEach(entry => {
    let element = document.createElement("div");
    if (entry["prize"] != null) {
      let image = document.createElement("img");
      image.src = getById(prizes, entry["prize"]).image;
      element.appendChild(image);
    }
    element.addEventListener("click", event => {
      const target = event.target;
      console.log(Array.from(target.parentElement.children));
      console.log(Array.from(target.parentElement.children).indexOf(target));
      const index = Array.from(target.parentElement.children).indexOf(target);
      if (board_editor_tool.mode == "insert") {
        putPrize(index);
      } else if (board_editor_tool.mode == "delete") {
        removePrize(index);
      }
    });
    grid.appendChild(element);
  });

  // Prizes list setup
  let entry_template = document.querySelector(".board_editor_prizes_list_entry");
  let list = editor.querySelector(".board_editor_prizes_list");
  list.innerText = "";
  prizes.forEach(prize => {
    const entry = entry_template.cloneNode(true);
    entry.querySelector(".prize_icon").src = prize.image;
    entry.querySelector(".prize_name").innerText = prize.name + "#";
    entry.querySelector(".prize_id").innerText = prize.id;
    list.appendChild(entry);
  });

  // Users list setup
  entry_template = document.querySelector(".board_editor_users_list_entry");
  list = editor.querySelector(".board_editor_users_list");
  list.innerText = "";
  let active_users = board["users"];
  Object.entries(active_users).forEach(([username, shots]) => {
    const entry = entry_template.cloneNode(true);
    entry.querySelector(".username").innerText = username;
    entry.querySelector("button").style.display = "none";
    entry.querySelector("input").value = shots;
    list.appendChild(entry);
  });
  users.forEach(user => {
    if (Object.keys(active_users).includes(user["username"])) {
      return;
    }
    const entry = entry_template.cloneNode(true);
    entry.querySelector(".username").innerText = user["username"];
    entry.querySelector(".active_user").style.display = "none";
    list.appendChild(entry);
  });
}

function putPrizeTool(button) {
  const board_id = last_board_edited;
  const board = getById(boards, board_id);
  if (board.shotsFiredBy.length > 0) {
    window.alrert("Нельзя редактировать поле");
    return;
  }
  board_editor_tool = {
    mode: "insert",
    prize: parseInt(button.parentElement.querySelector(".prize_id").innerText),
  };
}

function putPrize(index) {
  const board_id = last_board_edited;
  const board = getById(boards, board_id);
  const x = index % board["size"];
  const y = Math.floor(index / board["size"]);
  const prize_id = board_editor_tool.prize;
  let form_data = new FormData();
  form_data.append("x", x);
  form_data.append("y", y);
  form_data.append("board_id", board_id);
  form_data.append("prize_id", prize_id);
  fetch(HOST + "/api/putPrize",
    {
      method: "POST",
      body: form_data,
    }
  ).then(response => {
    if (response.ok) {
      board.contents[index].prize = prize_id;
    } else {
      response.text().then(error_text => window.alert(error_text));
    }
    rebuildBoardEditor();
  });
}

function removePrizeTool() {
  const board_id = last_board_edited;
  const board = getById(boards, board_id);
  if (board.shotsFiredBy.length > 0) {
    window.alrert("Нельзя редактировать поле");
    return;
  }
  board_editor_tool = {
    mode: "delete",
    prize: null,
  };
}

function removePrize(index) {
  const board_id = last_board_edited;
  const board = getById(boards, board_id);
  const x = index % board["size"];
  const y = Math.floor(index / board["size"]);
  let form_data = new FormData();
  form_data.append("x", x);
  form_data.append("y", y);
  form_data.append("board_id", board_id);
  fetch(HOST + "/api/clearPrize",
    {
      method: "POST",
      body: form_data,
    }
  ).then(response => {
    if (response.ok) {
      board.contents[index].prize = null;
    } else {
      response.text().then(error_text => window.alert(error_text));
    }
    rebuildBoardEditor();
  });
}

function addUser(button) {
  const username = button.parentElement.querySelector(".username").innerText;
  let form_data = new FormData();
  form_data.append("board_id", last_board_edited);
  form_data.append("username", username);
  const board_id = last_board_edited;
  fetch(HOST + "/api/addPlayer",
    {
      method: "POST",
      body: form_data,
    }
  ).then(
    response => {
      if (response.ok) {
        getById(boards, board_id)["users"][username] = 0;
      }
      rebuildBoardEditor();
    }
  );
}

function removeUser(button) {
  const username = button.parentElement.parentElement.querySelector(".username").innerText;
  let form_data = new FormData();
  form_data.append("board_id", last_board_edited);
  form_data.append("username", username);
  const board_id = last_board_edited;
  fetch(HOST + "/api/removePlayer",
    {
      method: "POST",
      body: form_data,
    }
  ).then(response => {
    if (response.ok) {
      delete getById(boards, board_id)["users"][username];
    } else {
      response.text().then(error_text => window.alert(error_text));
    }
    rebuildBoardEditor();
  });
}

function setShots(input) {
  const shots = parseInt(input.value);
  const username = input.parentElement.parentElement.querySelector(".username").innerText;
  const board_id = last_board_edited;
  let form_data = new FormData();
  form_data.append("board_id", last_board_edited);
  form_data.append("username", username);
  form_data.append("shots", shots);
  fetch(HOST + "/api/setNumberOfShots",
    {
      method: "POST",
      body: form_data,
    }
  ).then(response => {
    if (!response.ok) {
      response.text().then(error_text => window.alert(error_text));
    }
  });
}

function rebuildBoardEditor() {
  const board_id = last_board_edited;
  const board = getById(boards, board_id);

  const popup = document.getElementsByClassName("popup_container_hidden")[0];
  popup.hidden = false;
  popup.getElementsByClassName("popup_title")[0].innerHTML = "Редактор полей (" + board.name + ")";
  const board_editor = document.getElementsByClassName("board_editor")[0].cloneNode(true);
  const popup_body = popup.getElementsByClassName("popup_body")[0];
  popup_body.innerText = "";
  setupBoardEditor(board_editor, board_id);
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
  const prize = getById(prizes, prize_id);

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

async function fetchUsers() {
  let request = await fetch(HOST + "/api/users");
  return await request.json();
}

function getById(array, id) {
  return array.filter(item => item.id == id)[0];
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

fetchUsers().then(
  fetched_users => {
    users = fetched_users;
  }
);
