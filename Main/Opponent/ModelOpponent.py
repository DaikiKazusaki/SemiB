from .Opponent import OpponentBase

class ModelOpponent(OpponentBase):
    def __init__(self, model):
        self.model = model
    #↓抽象メソッドの実装
    def opponent_move(self, board):
        board_size = board.shape[0]
        action, _ = self.model.predict(board)   # 次の手を取得
        # x = action % board_size
        # y = (action // board_size) % board_size
        # z = action // (board_size * board_size)
        x = action % board_size
        y = action // board_size
        z = 0
        while z < board_size:
            if board[x, y, z] == 0:
                break
            z += 1
        if z >= board_size:
            print('Model Opponent: random move because of illegal move.')
            return None
        return (x, y, z)