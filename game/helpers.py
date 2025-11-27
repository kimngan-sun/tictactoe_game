# game/helpers.py
def checkWin(board):
    """Kiểm tra người thắng"""
    # Chuyển keys sang string nếu cần
    if 0 in board:
        board = {str(k): v for k, v in board.items()}
    
    win_conditions = [
        ['0', '1', '2'], ['3', '4', '5'], ['6', '7', '8'],  # hàng ngang
        ['0', '3', '6'], ['1', '4', '7'], ['2', '5', '8'],  # hàng dọc
        ['0', '4', '8'], ['2', '4', '6']  # đường chéo
    ]
    
    for condition in win_conditions:
        if board[condition[0]] and \
           board[condition[0]] == board[condition[1]] == board[condition[2]]:
            return board[condition[0]]
    
    return None

def isDraw(board):
    """Kiểm tra hòa"""
    if 0 in board:
        board = {str(k): v for k, v in board.items()}
    
    return all(board[str(i)] != '' for i in range(9))