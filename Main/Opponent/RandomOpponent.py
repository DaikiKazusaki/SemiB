import numpy as np
from .Opponent import OpponentBase
from Environment import Black, White, Empty

class RandomOpponent(OpponentBase):
    def opponent_move(self, board):
        # ボードサイズを取得
        board_size = board.shape[0]
        valid_moves = []

        # 有効な手を収集
        for x in range(board_size):
            for y in range(board_size):
                for z in range(board_size):
                    if board[x, y, z] == Empty:  # 空いているマスを探す
                        if z == 0 or board[x, y, z - 1] != Empty:  # 真下に駒があるか確認
                            valid_moves.append((x, y, z))

        # ランダムに有効な手を選択
        if valid_moves:
            return valid_moves[np.random.choice(len(valid_moves))]
        return None  # 有効な手がない場合
