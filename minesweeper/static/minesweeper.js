(function () {
    var boardStatus = {
        width: 10,
        height: 10
    };

    $("#controls").append($("<button class='btn btn-primary'>New Game</button>").on("click", function () {
        $("#board tbody").empty().append(createBoard(boardStatus.width, boardStatus.height));
        boardStatus.game = 'new';
    }));

    $("#board").on("click", "td", function () {
        var td = this;
        var x = $(td).index();
        var y = $(td).parent().index();
        if (boardStatus.game == 'new') {
            $.post("/game/new", {width: boardStatus.width, height: boardStatus.height, x: x, y: y},
                function (data) {
                    console.log("Id: " + data.game_id);
                }, "json");
            boardStatus.game = 'playing';
        } else if (boardStatus.game == 'playing') {
            $.post("/game/click", {x: x, y: y},
                function (data) {
                    console.log("Status: " + data.status);
                    $(td).addClass(data.status);
                }, "json");
        }
    });

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