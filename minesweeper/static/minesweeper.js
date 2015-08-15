(function () {
    var gameInfo = {};

    $("#newGame").on("click", newGame);

    $("#board").on("click", "td", function () {
        var td = this;
        var x = $(td).index();
        var y = $(td).parent().index();

        if ($(td).is(".empty, .flag")) {
            return;
        }

        if (gameInfo.status == 'new') {
            gameInfo.history = [];
            $.post("/game/new", {
                    width: gameInfo.width,
                    height: gameInfo.height,
                    mineProbability: gameInfo.mineProbability / 100,
                    x: x,
                    y: y
                },
                function (data) {
                    window.history.replaceState("", "Game " + data.game_id, "?game=" + data.game_id);
                    gameInfo.history.push({request: {action: "click", x: x, y: y}, response: data});
                    processClick(data);
                }, "json");
        } else if (gameInfo.status == 'playing') {
            $.post("/game/click", {x: x, y: y}, function (data) {
                gameInfo.history.push({request: {action: "click", x: x, y: y}, response: data});
                processClick(data);
            }, "json");
        }
    }).on("contextmenu", "td", function (ev) {
        var td = this;
        var x = $(td).index();
        var y = $(td).parent().index();
        if ((gameInfo.status == 'new' || gameInfo.status == 'playing') && !$(td).is(".empty")) {
            $.post("/game/toggle_flag", {x: x, y: y}, function () {
                gameInfo.history.push({request: {action: "toggle_flag", x: x, y: y}});
                $(td).toggleClass("flag");
            });
        }
        ev.preventDefault();
    });

    function newGame() {
        gameInfo.width = $("#boardWidth").val();
        gameInfo.height = $("#boardHeight").val();
        gameInfo.mineProbability = $("#mineProbability").val();
        gameInfo.status = 'new';
        $("#board").removeClass("won lost");
        $("#board tbody").empty().append(createBoard(gameInfo.width, gameInfo.height));
    }

    function processClick(data) {
        gameInfo.status = data.status;
        if (data.status == 'playing') {
            updateBoard(data.cells);
        } else {
            drawFullBoard(data.boardState);
            $("#board").addClass(data.status);
        }
    }

    function drawFullBoard(boardState) {
        for (var i = 0; i < gameInfo.height; i++) {
            for (var j = 0; j < gameInfo.width; j++) {
                getCell(j, i).empty().attr("class", boardState[i][j] ? "mine" : "empty")
            }
        }
    }

    function updateBoard(cells) {
        $.each(cells, function (i, cell) {
            var content = cell.neighbour_mines > 0 ? cell.neighbour_mines : "";
            getCell(cell.x, cell.y).attr("class", "empty").text(content);
        })
    }

    function getCell(x, y) {
        return $("#board tr").eq(y).children().eq(x);
    }

    function createBoard(width, height) {
        var content = [];
        for (var i = 0; i < height; i++) {
            var tr = $("<tr/>");
            for (var j = 0; j < width; j++) {
                tr.append("<td/>");
            }
            content.push(tr);
        }
        return content;
    }

    function replayActions(n) {
        newGame();
        for (var i = 0; i <= n && i < gameInfo.history.length; i++) {
            var action = gameInfo.history[i];
            if (action.request.action == 'click') {
                processClick(action.response);
            } else if (action.request.action == 'toggle_flag') {
                getCell(action.request.x, action.request.y).toggleClass("flag");
            }
        }
    }

    // resume old game if any
    var oldGame = window.location.search.match(/game=(\d+)/);
    if (oldGame && oldGame[1]) {
        $.get("/game/history", {id: oldGame[1]}, function (data) {
            gameInfo.width = data.width;
            gameInfo.height = data.height;
            gameInfo.history = data.history;
            replayActions(gameInfo.history.length);
        }, "json");
    }
})();