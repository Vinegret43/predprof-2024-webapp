// Крч надо:
// 1. Сделать, чтобы скрипт запрашивал данные об игровых полях с сервера, парсил
// их и затем уже генерировал HTML для игровых полей на основе полученных данных.
// Можно это делать с помощью createBoard, если чё. Генерацию HTML я прописал уже
// 2. Сделать, чтобы клетки в таблице отвечали на клики и посылали запрос на
// сервер, говоря, что игрок хочет совершить выстрел. Я оставил TODO там,
// где надо добавить коллбэк (Только для клеток, в которые ещё не стреляли,
// само собой). Эта самая клетка потом ещё должна будет обновить себя
// взависимости от полученного с сервака результата

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
                // TODO: Attach a callback to `entry` to react to clicks
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
