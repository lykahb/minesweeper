import random
from pyramid.response import Response
from pyramid.view import view_config

from .models import (
    DBSession,
    Game,
    PlayerAction,
    PlayerActionEnum, GameStatusEnum)


# Creates a board with given dimensions that has no mines on the start position
def create_new_game(width, height, mines_count):
    board = [[0 for _ in range(width)] for _ in range(height)]
    visited_cells = [[False for _ in range(width)] for _ in range(height)]
    return Game(status=GameStatusEnum.new.value, width=width, height=height, board_state=board,
                visited_cells=visited_cells, mines_count=mines_count)


def initialize_board(game, start_x, start_y):
    coords = set()
    for y in range(game.height):
        for x in range(game.width):
            coords.add((x, y))
    coords.remove((start_x, start_y))
    for (x, y) in random.sample(coords, game.mines_count):
        game.board_state[y][x] = True
    DBSession.query(Game).filter(Game.id == game.id).update({Game.board_state: game.board_state})


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
    width = len(game.board_state[0])
    height = len(game.board_state)
    game.visited_cells = [[False for _ in range(width)] for _ in range(height)]
    history = []
    for action in actions:
        result = {'request': {'action': action.action, 'x': action.x, 'y': action.y}}
        if action.action == PlayerActionEnum.click.value:
            result['response'] = process_click(game, action.x, action.y)
        history.append(result)
    return {'width': width, 'height': height, 'history': history}


@view_config(route_name='new_game', renderer='json')
def new_game(request):
    width = int(request.POST['width'])
    height = int(request.POST['height'])
    mines_count = float(request.POST['minesCount'])
    game = create_new_game(width, height, mines_count)
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
    if game.status == GameStatusEnum.new.value:
        initialize_board(game, x, y)
        game.status = GameStatusEnum.playing.value

    if game.status != GameStatusEnum.playing.value or game.visited_cells[y][x]:
        return Response('Invalid request', content_type='text/plain', status_int=500)
    DBSession.add(PlayerAction(game_id=game.id, action=PlayerActionEnum.click.value, x=x, y=y))
    result = process_click(game, x, y)
    game.status = result['status']
    DBSession.query(Game).filter(Game.id == game.id).update({Game.visited_cells: game.visited_cells})
    return result


def process_click(game, x, y):
    if game.board_state[y][x]:
        return {'status': GameStatusEnum.lost.value, 'boardState': game.board_state}
    else:
        cells = []

        def traverse(x, y):
            if game.visited_cells[y][x]:
                return
            game.visited_cells[y][x] = True

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

        sum_visited = 0
        for row in game.visited_cells:
            sum_visited += sum(row)
        if sum_visited + game.mines_count == len(game.board_state) * len(game.board_state[0]):
            return {'status': GameStatusEnum.won.value, 'boardState': game.board_state}
        else:
            return {'status': GameStatusEnum.playing.value, 'cells': cells}


@view_config(route_name='toggle_flag', renderer='json')
def toggle_flag(request):
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    game = DBSession.query(Game).get(request.session['current_game'])

    if x < 0 or x >= len(game.board_state[0]) or y < 0 or y >= len(game.board_state):
        return Response('Coordinates out of range', content_type='text/plain', status_int=500)

    DBSession.add(PlayerAction(game_id=game.id, action=PlayerActionEnum.toggle_flag.value, x=x, y=y))
