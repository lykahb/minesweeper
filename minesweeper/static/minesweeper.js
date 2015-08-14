(function () {
    $("#board").text("game");

    $("#controls").append($("<button>New Game</button>").on("click", function () {
        $.post("/game/new", {width: 10, height: 10, x: 0, y: 0}, function () {
            console.log("new game");
        })
    }));
})();