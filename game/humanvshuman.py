class HvsH:
    def __init__(self):
        self.size = 9
        self.board = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 'X'
        self.winner = None
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
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
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

    def reset(self):
        self.board = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False