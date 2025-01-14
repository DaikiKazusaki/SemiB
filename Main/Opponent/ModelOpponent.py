from Opponent import Opponent

class ModelOponent(Opponent):
    def __init__(self, model):
        self.model = model      # モデルを受け取る

    #↓抽象メソッドの実装
    def opponent_move(self, board):
        action, _ = self.model.predict(board)   # 次の手を取得
        env = self.model.get_env()              # Environmentを取得
        x = action % env.board_size
        y = (action // env.board_size) % env.board_size
        z = action // (env.board_size * env.board_size)
        return (x, y, z)