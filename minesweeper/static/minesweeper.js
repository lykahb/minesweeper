(function () {
    var gameInfo = {};

    $("#newGame").on("click", function () {
        gameInfo.history = [];
        newGame();
        $.post("/game/new", {
                width: gameInfo.width,
                height: gameInfo.height,
                minesCount: gameInfo.minesCount
            },
            function (data) {
                window.history.replaceState("", "Game " + data.game_id, "?game=" + data.game_id);
            }, "json");
    });

    $("#board").on("click", "td", function () {
        var td = this;
        var x = $(td).index();
        var y = $(td).parent().index();

        if ($(td).is(".empty, .flag")) {
            return;
        }

        if (gameInfo.status == 'playing') {
            $.post("/game/click", {x: x, y: y}, function (data) {
                gameInfo.history.push({request: {action: "click", x: x, y: y}, response: data});
                processClick(data);
            }, "json");
        }
    }).on("contextmenu", "td", function (ev) {
        var td = this;
        var x = $(td).index();
        var y = $(td).parent().index();

        if (gameInfo.status == 'playing' && !$(td).is(".empty")) {
            $.post("/game/toggle_flag", {x: x, y: y}, function () {
                gameInfo.history.push({request: {action: "toggle_flag", x: x, y: y}});
                $(td).toggleClass("flag glyphicon glyphicon-flag");
            });
        }
        ev.preventDefault();
    });

    $("#showReplay").on("click", function () {
        replayActions(gameInfo.history.length, 500);
    });

    $("#boardWidth, #boardHeight").on("change", function () {
        var max = Math.floor($("#boardWidth").val() * $("#boardHeight").val() * 2 / 3);
        var count = $("#minesCount").val();
        $("#minesCount").attr("max", max).val(Math.min(max, count));
    });
    function newGame() {
        gameInfo.width = $("#boardWidth").val();
        gameInfo.height = $("#boardHeight").val();
        gameInfo.minesCount = $("#minesCount").val();
        gameInfo.status = 'playing';
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
                getCell(j, i).empty().attr("class", boardState[i][j] ? "mine glyphicon glyphicon-certificate" : "empty")
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

    function replayActions(n, delay) {
        newGame();
        var i = 0;
        var next = function () {
            if (!(i <= n && i < gameInfo.history.length)) {
                return;
            }
            var action = gameInfo.history[i];
            if (action.request.action == 'click') {
                processClick(action.response);
            } else if (action.request.action == 'toggle_flag') {
                getCell(action.request.x, action.request.y).toggleClass("flag glyphicon glyphicon-flag");
            }
            i++;
            setTimeout(next, delay);
        };
        next();
    }

    // resume old game if any
    var oldGame = window.location.search.match(/game=(\d+)/);
    if (oldGame && oldGame[1]) {
        $.get("/game/history", {id: oldGame[1]}, function (data) {
            $("#boardWidth").val(data.width);
            $("#boardHeight").val(data.height);
            gameInfo.history = data.history;
            replayActions(gameInfo.history.length);
        }, "json");
    }
})();