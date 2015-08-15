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


@view_config(route_name='game_history', renderer='json')
def game_history(request):
    game_id = request.GET['id']
    request.session['current_game'] = game_id
    actions = DBSession.query(PlayerAction).filter(PlayerAction.game_id == game_id) \
        .order_by(PlayerAction.timestamp)
    game = DBSession.query(Game).get(game_id)
    history = []
    for action in actions:
        result = {'request': {'action': action.action, 'x': action.x, 'y': action.y}}
        if action.action == PlayerActionEnum.click.value:
            result['response'] = process_click(game, action.x, action.y)
        history.append(result)
    return {'width': len(game.board_state[0]), 'height': len(game.board_state), 'history': history}


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
    result = process_click(game, x, y)
    DBSession.add(PlayerAction(game_id=game.id, action=PlayerActionEnum.click.value, x=x, y=y))
    result['game_id'] = game.id
    return result


@view_config(route_name='click', renderer='json')
def click(request):
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    game = DBSession.query(Game).get(request.session['current_game'])
    if x < 0 or x >= len(game.board_state[0]) or y < 0 or y >= len(game.board_state):
        return Response('Coordinates out of range', content_type='text/plain', status_int=500)
    DBSession.add(PlayerAction(game_id=game.id, action=PlayerActionEnum.click.value, x=x, y=y))
    result = process_click(game, x, y)
    game.status = result['status']
    return result


def process_click(game, x, y):
    if game.board_state[y][x]:
        return {'status': GameStatusEnum.lost.value, 'boardState': game.board_state}
    else:
        cells = []
        visited = set()

        def traverse(x, y):
            if (x, y) in visited:
                return
            visited.add((x, y))

            def visit_neighbours(f, acc=None):
                for i in range(y - 1, y + 2):
                    for j in range(x - 1, x + 2):
                        if i < 0 or i >= len(game.board_state) or j < 0 or j >= len(game.board_state[0]):
                            continue
                        acc = f(i, j, acc)
                return acc

            neighbour_mines = visit_neighbours(lambda i, j, acc: acc + 1 if game.board_state[i][j] else acc, 0)

            cells.append({'x': x, 'y': y, 'neighbour_mines': neighbour_mines})
            if neighbour_mines == 0:
                visit_neighbours(lambda i, j, _: traverse(j, i))

        traverse(x, y)
        return {'status': GameStatusEnum.playing.value, 'cells': cells}


@view_config(route_name='toggle_flag', renderer='json')
def toggle_flag(request):
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    game = DBSession.query(Game).get(request.session['current_game'])

    if x < 0 or x >= len(game.board_state[0]) or y < 0 or y >= len(game.board_state):
        return Response('Coordinates out of range', content_type='text/plain', status_int=500)

    DBSession.add(PlayerAction(game_id=game.id, action=PlayerActionEnum.toggle_flag.value, x=x, y=y))
