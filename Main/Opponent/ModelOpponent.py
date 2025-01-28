from .Opponent import OpponentBase
from Environment import Empty

class ModelOpponent(OpponentBase):
    def __init__(self, model):
        self.model = model
    #↓抽象メソッドの実装
    def opponent_move(self, board):
        board_size = board.shape[0]
        action, _ = self.model.predict(board)   # 次の手を取得
        x = action % board_size
        y = action // board_size
        z = 0
        while z < board_size:
            if board[x, y, z] == Empty:
                break
            z += 1
        if z >= board_size:
            return None
        return (x, y, z)