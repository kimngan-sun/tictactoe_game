class TicTacToe:
    def __init__(self, difficulty='medium'):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.difficulty = difficulty
        self.depths = {
            'easy': 1,
            'medium': 2,
            'hard': 3
        }
        self.game_over = False

    def make_move(self, row, col):
        if self.board[row][col] == '' and not self.game_over:
            self.board[row][col] = self.current_player

            # Check for winner
            if self.check_winner():
                self.winner = self.current_player
                self.game_over = True
            # Check for tie
            elif self.is_board_full():
                self.game_over = True
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
        return False

    def check_winner(self):
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return True

        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return True

        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return True

        return False

    def is_board_full(self):
        return all(cell != '' for row in self.board for cell in row)

    def get_empty_cells(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == '']

    def evaluate_board(self):
        # Check rows
        for row in self.board:
            if row.count('O') == 3:
                return 1
            if row.count('X') == 3:
                return -1

        # Check columns
        for col in range(3):
            if all(self.board[row][col] == 'O' for row in range(3)):
                return 1
            if all(self.board[row][col] == 'X' for row in range(3)):
                return -1

        # Check diagonals
        if all(self.board[i][i] == 'O' for i in range(3)):
            return 1
        if all(self.board[i][i] == 'X' for i in range(3)):
            return -1
        if all(self.board[i][2-i] == 'O' for i in range(3)):
            return 1
        if all(self.board[i][2-i] == 'X' for i in range(3)):
            return -1

        return 0

    def minimax(self, depth, alpha, beta, is_maximizing):
        if self.check_winner():
            return -1 if is_maximizing else 1
        if self.is_board_full():
            return 0
        if depth == 0:
            return 0

        if is_maximizing:
            max_eval = float('-inf')
            for i, j in self.get_empty_cells():
                self.board[i][j] = 'O'
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.board[i][j] = ''
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for i, j in self.get_empty_cells():
                self.board[i][j] = 'X'
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.board[i][j] = ''
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self):
        if self.difficulty == 'easy':
            # In easy mode, sometimes make random moves
            import random
            if random.random() < 0.3:  # 30% chance of random move
                empty_cells = self.get_empty_cells()
                if empty_cells:
                    return random.choice(empty_cells)

        # For medium and hard, use minimax with different depths
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        depth = self.depths[self.difficulty]

        # First, check if we need to block opponent's winning move
        for i, j in self.get_empty_cells():
            self.board[i][j] = 'X'
            if self.check_winner():
                self.board[i][j] = ''
                return (i, j)
            self.board[i][j] = ''

        # Then, check if we can win
        for i, j in self.get_empty_cells():
            self.board[i][j] = 'O'
            if self.check_winner():
                self.board[i][j] = ''
                return (i, j)
            self.board[i][j] = ''

        # If no immediate win or block, use minimax
        for i, j in self.get_empty_cells():
            self.board[i][j] = 'O'
            score = self.minimax(depth, alpha, beta, False)
            self.board[i][j] = ''

            if score > best_score:
                best_score = score
                best_move = (i, j)

        return best_move

    def reset(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False