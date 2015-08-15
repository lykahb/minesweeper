(function () {
    var gameInfo = {
        width: 10,
        height: 10
    };

    $("#controls").append($("<button class='btn btn-primary'>New Game</button>").on("click", function () {
        $("#board tbody").empty().append(createBoard(gameInfo.width, gameInfo.height));
        gameInfo.status = 'new';
    }));

    $("#board").on("click", "td", function () {
        var td = this;
        var x = $(td).index();
        var y = $(td).parent().index();

        function processClick(data) {
            gameInfo.status = data.status;
            if (data.status == 'lost') {
                drawLostBoard(data.boardState);
            } else {
                updateBoard(data.cells);
            }
        }
        if ($(td).is(".empty, .flag")) {
            return;
        }

        if (gameInfo.status == 'new') {
            $.post("/game/new", {width: gameInfo.width, height: gameInfo.height, x: x, y: y},
                function (data) {
                    console.log("Id: " + data.game_id);
                    processClick(data);
                }, "json");
        } else if (gameInfo.status == 'playing') {
            $.post("/game/click", {x: x, y: y}, processClick, "json");
        }
    }).on("contextmenu", "td", function (ev) {
        var td = this;
        var x = $(td).index();
        var y = $(td).parent().index();
        if ((gameInfo.status == 'new' || gameInfo.status == 'playing') && !$(td).is(".empty")) {
            $(td).toggleClass("flag");
            $.post("/game/toggle_flag", {x: x, y: y});
        }
        ev.preventDefault();
    });

    function drawLostBoard(boardState) {
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
})();