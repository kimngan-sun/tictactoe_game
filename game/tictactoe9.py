import random

class TicTacToe9:
    def __init__(self, difficulty='medium'):
        self.size = 9
        self.board = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 'X'
        self.winner = None
        self.difficulty = difficulty
        self.depths = {
            'easy': 1,
            'medium': 2,
            'hard': 3
        }
        self.game_over = False
        self.win_length = 5

    def make_move(self, row, col):
        if self.board[row][col] == '' and not self.game_over:
            self.board[row][col] = self.current_player
            if self.check_winner(row, col):
                self.winner = self.current_player
                self.game_over = True
            elif self.is_board_full():
                self.game_over = True
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
        return False

    def check_winner(self, row, col):
        # Check all directions for 5 in a row
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        player = self.board[row][col]
        for dr, dc in directions:
            count = 1
            for d in [1, -1]:
                r, c = row, col
                while True:
                    r += dr * d
                    c += dc * d
                    if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                        count += 1
                    else:
                        break
            if count >= self.win_length:
                return True
        return False

    def is_board_full(self):
        return all(cell != '' for row in self.board for cell in row)

    def get_empty_cells(self):
        # Only consider cells near existing pieces (within 1 cell)
        candidates = set()
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != '':
                    for di in range(-1, 2):
                        for dj in range(-1, 2):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.size and 0 <= nj < self.size:
                                if self.board[ni][nj] == '':
                                    candidates.add((ni, nj))
        if not candidates:
            # If board is empty, allow all
            return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == '']
        return list(candidates)

    def evaluate_board(self):
        # Heuristic: count open lines of 2, 3, 4, 5 for both players
        def count_lines(player):
            score = 0
            for dr, dc in [(1,0), (0,1), (1,1), (1,-1)]:
                for i in range(self.size):
                    for j in range(self.size):
                        count = 0
                        open_ends = 0
                        for k in range(self.win_length):
                            ni, nj = i + dr*k, j + dc*k
                            if 0 <= ni < self.size and 0 <= nj < self.size:
                                if self.board[ni][nj] == player:
                                    count += 1
                                elif self.board[ni][nj] != '':
                                    count = -99
                                    break
                            else:
                                count = -99
                                break
                        if count > 0:
                            # Check open ends
                            before_i, before_j = i - dr, j - dc
                            after_i, after_j = i + dr*self.win_length, j + dc*self.win_length
                            if 0 <= before_i < self.size and 0 <= before_j < self.size and self.board[before_i][before_j] == '':
                                open_ends += 1
                            if 0 <= after_i < self.size and 0 <= after_j < self.size and self.board[after_i][after_j] == '':
                                open_ends += 1
                            if count == 5:
                                score += 100000
                            elif count == 4 and open_ends > 0:
                                score += 1000
                            elif count == 3 and open_ends > 0:
                                score += 100
                            elif count == 2 and open_ends > 0:
                                score += 10
            return score
        return count_lines('O') - count_lines('X')

    def minimax(self, depth, alpha, beta, is_maximizing):
        if self.winner == 'O':
            return 100000
        if self.winner == 'X':
            return -100000
        if self.is_board_full() or depth == 0:
            return self.evaluate_board()

        if is_maximizing:
            max_eval = float('-inf')
            for i, j in self.get_empty_cells():
                self.board[i][j] = 'O'
                prev_winner = self.winner
                if self.check_winner(i, j):
                    self.winner = 'O'
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.board[i][j] = ''
                self.winner = prev_winner
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for i, j in self.get_empty_cells():
                self.board[i][j] = 'X'
                prev_winner = self.winner
                if self.check_winner(i, j):
                    self.winner = 'X'
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.board[i][j] = ''
                self.winner = prev_winner
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self):
        if self.difficulty == 'easy':
            if random.random() < 0.3:
                empty_cells = self.get_empty_cells()
                if empty_cells:
                    return random.choice(empty_cells)

        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        depth = self.depths[self.difficulty]

        # Block opponent's win
        for i, j in self.get_empty_cells():
            self.board[i][j] = 'X'
            if self.check_winner(i, j):
                self.board[i][j] = ''
                return (i, j)
            self.board[i][j] = ''
        # Try to win
        for i, j in self.get_empty_cells():
            self.board[i][j] = 'O'
            if self.check_winner(i, j):
                self.board[i][j] = ''
                return (i, j)
            self.board[i][j] = ''

        for i, j in self.get_empty_cells():
            self.board[i][j] = 'O'
            score = self.minimax(depth, alpha, beta, False)
            self.board[i][j] = ''
            if score > best_score:
                best_score = score
                best_move = (i, j)
        return best_move

    def reset(self):
        self.board = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False 