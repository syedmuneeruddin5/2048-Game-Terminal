# 2048 Game in Terminal

import curses
import os
import random
import time
from math import log2

ROWS,COLS = 4,4
MODE = '2048'   # Available Modes : '2048' and 'endless'
SCREEN_WIDTH = os.get_terminal_size().columns

COLORS = {
        2: (238, 228, 218),
        4: (238, 225, 201),
        8: (243, 178, 122),
        16: (246, 150, 100),
        32: (247, 124, 95),
        64: (247, 95, 59),
        128: (237, 208, 115),
        256: (236, 203, 96),
        512: (236, 200, 80),
        1024: (236, 196, 65),
        2048: (235, 193, 45),
        4096: (239, 102, 109),
        8192: (237, 77, 89),
        16384: (225, 67, 56),
        32768: (114, 180, 214),
        65536: (92, 160, 223),
        'higher': (92, 160, 223)
    }

DEFAULT_COLOR = -1

def set_colors():

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    for pair_id, (value, rgb) in enumerate(COLORS.items(), start=5):

        color_id = 100 - pair_id

        r, g, b = (int(color * (1000 / 255)) for color in rgb)

        curses.init_color(color_id, r, g, b)
        curses.init_pair(pair_id, color_id, curses.COLOR_BLACK)

def start_information(stdscr):

    stdscr.clear()
    stdscr.addstr('\n')
    stdscr.addstr('2048 Game'.center(SCREEN_WIDTH) + '\n', curses.A_BOLD)
    stdscr.addstr('To play, use the arrow keys or keys w, a, s and d.'.center(SCREEN_WIDTH) + '\n', curses.A_BOLD)
    stdscr.addstr('To quit press q.'.center(SCREEN_WIDTH) + '\n', curses.A_BOLD)
    stdscr.addstr('To restart press r.'.center(SCREEN_WIDTH) + '\n', curses.A_BOLD)
    stdscr.addstr('Press enter to start.'.center(SCREEN_WIDTH) + '\n', curses.A_BOLD)
    stdscr.refresh()

    while True:

        key = stdscr.getch()
        if key == ord('\n'):
            break

def display_board(stdscr, board, game_status):


    BOARD_WIDTH = (8 * COLS) + 1
    CENTER_ALIGN = ' ' * int((SCREEN_WIDTH - BOARD_WIDTH) / 2)

    GREEN_pair_number = 2
    RED_pair_number = 3

    stdscr.clear()

    stdscr.addstr('\n' + (CENTER_ALIGN) + '-' * BOARD_WIDTH + '\n')
    stdscr.addstr((CENTER_ALIGN) + ('|' + ' ' * 7) * (COLS + 1) + '\n')

    for i in range(ROWS):

        stdscr.addstr(CENTER_ALIGN)

        for j in range(COLS):

            value = board[i][j]

            if value != 0:
                if value in COLORS.keys():
                    pair_number = int(log2(value)) + 4
                else:
                    pair_number = len(COLORS) + 4

                text = str(value).center(5)

            else:
                text = ' ' * 5
                pair_number = 1

            stdscr.addstr('|')
            stdscr.addstr(f' {text} ', curses.A_BOLD | curses.color_pair(pair_number))

        stdscr.addstr('|' + '\n')
        stdscr.addstr( CENTER_ALIGN + ( '|' + ' ' * 7) * (COLS + 1) + '\n')
        stdscr.addstr( CENTER_ALIGN + '-' * BOARD_WIDTH + '\n')

        if i < ROWS - 1:
            stdscr.addstr( CENTER_ALIGN + ('|' + ' ' * 7) * (COLS + 1) + '\n')

    stdscr.addstr('\n')

    if game_status == 'win':
        stdscr.addstr(CENTER_ALIGN + 'You Win'.center(BOARD_WIDTH) + '\n', curses.color_pair(GREEN_pair_number) | curses.A_BOLD)

    elif game_status == 'lose':
        stdscr.addstr(CENTER_ALIGN + 'You Lose'.center(BOARD_WIDTH) + '\n', curses.color_pair(RED_pair_number) | curses.A_BOLD)

    stdscr.refresh()

def transpose_board(board):

    transposed_board = []

    for col in range(len(board[0])):

        row_list = []
        for row in range(len(board)):
            row_list.append(board[row][col])

        transposed_board.append(row_list)

    return transposed_board

def generate_tiles(board, no_of_tiles = 1, four_included = True):

    empty_positions = []

    for i in range(len(board)):
        for j in range(len(board[0])):

            if board[i][j] == 0:
                empty_positions.append((i,j))

    if len(empty_positions) >= no_of_tiles:

        for _ in range(no_of_tiles):

            random_pos = random.choice(empty_positions)
            row,col = random_pos

            if four_included:
                value = random.choice([2 for _ in range(9)]+[4])

            else: value = 2

            board[row][col] = value
            empty_positions.remove((row,col))

def reverse_board(board):

    reversed_board = []
    for row in board:
        reversed_board.append(list(reversed(row)))

    return reversed_board

def move_tiles(board:list, pos:tuple):

    row,col = pos
    no_of_cols = len(board[row])

    if board[row][col : ] != [0 for _ in range(no_of_cols - col)]:

        board[row].pop(col)
        board[row].append(0)

        return True

    else:
        return False

def update_board(board, direction):

    pseudo_direction = {'up':'left', 'down':'right'}

    if direction in pseudo_direction.keys():

        transposed_board = transpose_board(board)

        move = update_board(transposed_board, pseudo_direction[direction])
        updated_board = move['board']
        updated = move['updated']

        reordered_board = transpose_board(updated_board)

        return {'board': reordered_board, 'updated': updated}

    elif direction == 'right':

        reversed_board = reverse_board(board)

        move = update_board(reversed_board, 'left')
        updated_board = move['board']
        updated = move['updated']

        reordered_board = reverse_board(updated_board)

        return {'board': reordered_board, 'updated': updated}

    elif direction == 'left':

        updated = False

        rows = len(board)
        cols = len((board[0]))

        for i in range(rows):
            for j in range(cols - 1, -1, -1):

                if board[i][j] == 0:
                    if move_tiles(board, (i,j)) :
                        updated = True

        for i in range(rows):
            for j in range(cols - 1):

                tile = board[i][j]
                next_tile = board[i][j+1]

                if tile != 0 and tile == next_tile:

                    board[i][j] *= 2
                    board[i][j+1] = 0

                    move_tiles(board, (i,j+1))
                    updated = True

        return {'board' : board, 'updated' : updated}

def check_win(board):

    if MODE == '2048':
        for i in board:
            for j in i:
                if j == 2048:
                    return True

    return False

def check_lose(board):

    for i in range(len(board)):
        for j in range(len(board[0])):

            if board[i][j] == 0:
                return False


    for i in range(ROWS):
        for j in range(COLS):

            tile =  board[i][j]

            if j < COLS - 1:
                beside_tile = board[i][j+1]

                if tile == beside_tile:
                    return False

            if i < ROWS - 1:

                down_tile = board[i+1][j]

                if tile == down_tile:
                    return False

    return True

def main(stdscr):

    stdscr.clear()
    curses.curs_set(0)
    set_colors()

    start_information(stdscr)

    board = [[0 for col in range(COLS)] for row in range(ROWS)]
    game_status = None

    generate_tiles(board,2,False)
    display_board(stdscr, board, game_status)

    keybindings = {
        ord('w'): 'up'   , curses.KEY_UP : 'up',
        ord('s'): 'down' , curses.KEY_DOWN : 'down',
        ord('a'): 'left' , curses.KEY_LEFT : 'left',
        ord('d'): 'right', curses.KEY_RIGHT : 'right'
    }

    while True:
        key = stdscr.getch()

        if key == ord('q'):
            break

        elif key == ord('r'):
            main(stdscr)
            break

        elif key in keybindings:

            make_move = update_board(board, keybindings[key])
            board = make_move['board']
            updated = make_move['updated']

            if updated:

                display_board(stdscr, board, game_status)

                generate_tiles(board)

                time.sleep(1/5)
                display_board(stdscr, board, game_status)

                if check_win(board):
                    game_status = 'win'
                    break

                elif check_lose(board):
                    game_status = 'lose'
                    break

    if key not in [ord('q'),ord('r')]:

        while True :

            display_board(stdscr, board, game_status)

            key = stdscr.getch()

            if key == ord('q'):
                break

            elif key == ord('r'):
                main(stdscr)
                break



curses.wrapper(main)