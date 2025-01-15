import numpy as np
from Opponent import Opponent

class StrongOpponent(Opponent):
    def opponent_move(self, board):
        board_size = board.shape[0]
        directions = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1), 
            (1, 1, 0), (1, -1, 0), (1, 0, 1), 
            (1, 0, -1), (0, 1, 1), (0, 1, -1), 
            (1, 1, 1), (1, 1, -1), (1, -1, 1), 
            (1, -1, -1)
        ]

        def is_winning_move(x, y, z, player):
            """指定位置で勝利条件を満たすかを確認"""
            for dx, dy, dz in directions:
                count = 1
                for step in range(1, 4):
                    nx, ny, nz = x + step * dx, y + step * dy, z + step * dz
                    if 0 <= nx < board_size and 0 <= ny < board_size and 0 <= nz < board_size:
                        if board[nx, ny, nz] == player:
                            count += 1
                        else:
                            break
                    else:
                        break
                for step in range(1, 4):
                    nx, ny, nz = x - step * dx, y - step * dy, z - step * dz
                    if 0 <= nx < board_size and 0 <= ny < board_size and 0 <= nz < board_size:
                        if board[nx, ny, nz] == player:
                            count += 1
                        else:
                            break
                    else:
                        break
                if count >= 4:
                    return True
            return False

        # 優先順位で手を選択
        valid_moves = []
        for x in range(board_size):
            for y in range(board_size):
                for z in range(board_size):
                    if board[x, y, z] == 0 and (z == 0 or board[x, y, z - 1] != 0):
                        valid_moves.append((x, y, z))

        # 自分が勝てる手を優先
        for x, y, z in valid_moves:
            if is_winning_move(x, y, z, 1):  # 自分の色が黒（1）として判断
                return x, y, z

        # 相手の勝ちを阻止
        for x, y, z in valid_moves:
            if is_winning_move(x, y, z, -1):  # 相手の色が白（-1）として判断
                return x, y, z

        # ランダムに置く（ここを改良して更に賢い戦略を加えることも可能）
        if valid_moves:
            return valid_moves[np.random.choice(len(valid_moves))]
        return None
