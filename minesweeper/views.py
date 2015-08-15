import random
from pyramid.response import Response
from pyramid.view import view_config

from .models import (
    DBSession,
    Game,
    PlayerAction,
    PlayerActionEnum, GameStatusEnum)


# Creates a board with given dimensions that has no mines on the start position
def init_game_state(width, height, start_x, start_y):
    mine_probability = 0.3
    board = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            board[y][x] = random.random() < mine_probability and not (x == start_x and y == start_y)
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
    request.session['current_game'] = game.id
    return {'game_id': game.id}


@view_config(route_name='click', renderer='json')
def click(request):
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    game = DBSession.query(Game).get(request.session['current_game'])

    if x < 0 or x >= len(game.board_state[0]) or y < 0 or y >= len(game.board_state):
        return Response('Coordinates out of range', content_type='text/plain', status_int=500)

    DBSession.add(PlayerAction(game_id=game.id, action=PlayerActionEnum.click.value, x=x, y=y))
    game.status = GameStatusEnum.lost.value
    if game.board_state[y][x]:
        game.status = GameStatusEnum.lost.value
        return {'status': 'mine'}
    else:
        return {'status': 'empty'}


@view_config(route_name='toggle_flag', renderer='json')
def toggle_flag(request):
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    game = DBSession.query(Game).get(request.session['current_game'])

    if x < 0 or x >= len(game.board_state[0]) or y < 0 or y >= len(game.board_state):
        return Response('Coordinates out of range', content_type='text/plain', status_int=500)

    DBSession.add(PlayerAction(game_id=game.id, action=PlayerActionEnum.flag.value, x=x, y=y))
