import random
from pyramid.view import view_config


from .models import (
    DBSession,
    Game,
    PlayerAction,
    CellState)


# Creates a board with given dimensions that has no mines on the start position
def init_game_state(width, height, start_x, start_y):
    mine_probability = 0.3
    board = [[0 for _ in range(width)] for _ in range(height)]
    for x in range(width):
        for y in range(height):
            if x == start_x and y == start_y:
                board[x][y] = CellState.empty.value
            else:
                board[x][y] = CellState.mine.value if random.random() < mine_probability else CellState.empty.value
    return board


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {}


@view_config(route_name='new_game', renderer='json')
def new_game(request):
    width = int(request.POST['width'])
    height = int(request.POST['height'])
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    game = Game(board_state=init_game_state(width, height, x, y))
    DBSession.add(game)
    DBSession.flush()
    return {'game_id': game.id}
