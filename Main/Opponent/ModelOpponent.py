from Opponent import OpponentBase

class ModelOpponent(OpponentBase):
    def __init__(self, model, env):
        self.env = env
        self.model = model      # モデルを受け取る

    #↓抽象メソッドの実装
    def opponent_move(self, board):
        action, _ = self.model.predict(board)   # 次の手を取得
        x = action % self.env.board_size
        y = (action // self.env.board_size) % self.env.board_size
        z = action // (self.env.board_size * self.env.board_size)
        return (x, y, z)