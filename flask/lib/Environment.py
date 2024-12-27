# 立体4目並べのEnvironment
import gymnasium as gym
import numpy as np
from .model import sample_model  # TODO: 本実装では model を import

BOARD_SIZE = 4

# Environmentは
#   1. 訓練用(OpponentMoveがランダム)
#   2. 実際に人との対戦用(OpponentMoveが、強化学習によるモデルの予測値)
# の二つが入りそう、コンストラクタで指定すれば良さそう？

# 以下はサンプル用のEnvironmentで、本実装では用いない
class SampleEnv():
    def __init__(self):
        self.board_size = BOARD_SIZE
        self.board = None
        self.reward = 0
        self.color = 1              # 黒色
    
    def reset(self):
        self.board = np.zeros((self.board_size, self.board_size, self.board_size), dtype=int)
        self.reward = 0
        pass

    def step(self, action):
        x = (action % (self.board_size ** 2)) % self.board_size
        y = (action % (self.board_size ** 2)) // self.board_size
        z = action // (self.board_size ** 2)
        # 本来のEnvironmentならここでactionがinvalidかどうかを確認する
        self.board[x, y, z] = 1     # 黒
        if self.is_game_over():
            return self.board.copy(), self.reward, True, False, {}
        move = self.opponent_move()
        info = { "opponent": move }
        if self.is_game_over():
            return self.board.copy(), self.reward, True, False, info
        return self.board.copy(), self.reward, False, False, info

    def opponent_move(self):
        x, y, z = sample_model.predict(self.board)
        self.board[x, y, z] = -1    # 白
        return (x, y, z)

    def is_game_over(self):
        # 1. X面, Y面, Z面ごとに見る
        # 2. 斜めを見る
        for x in range(self.board_size):
            # 1. Yを固定
            # 2. Zを固定
            # 3. 斜め
            for y in range(self.board_size):
                sum = self.board[x, y, :].sum()     # 足すことで全部白か黒か判定可能
                if np.abs(sum) == self.board_size:
                    self.reward = 1 if sum > 0 else -1  # メソッド化すべき
                    return True
            for z in range(self.board_size):
                sum = self.board[x, :, z].sum()
                if np.abs(sum) == self.board_size:
                    self.reward = 1 if sum > 0 else -1
                    return True
            sum_cross_1 = np.diag(self.board[x]).sum()  # 対角成分
            if np.abs(sum_cross_1) == self.board_size:
                self.reward = 1 if sum_cross_1 > 0 else -1
                return True
            sum_cross_2 = np.diag(np.fliplr(self.board[x])).sum()   # 左下から右上の要素の合計
            if np.abs(sum_cross_2) == self.board_size:
                self.reward = 1 if sum_cross_2 > 0 else -1
                return True
        for y in range(self.board_size):
            for x in range(self.board_size):
                sum = self.board[x, y, :].sum()     # 足すことで全部白か黒か判定可能
                if np.abs(sum) == self.board_size:
                    self.reward = 1 if sum > 0 else -1  # メソッド化すべき
                    return True
            for z in range(self.board_size):
                sum = self.board[:, y, z].sum()
                if np.abs(sum) == self.board_size:
                    self.reward = 1 if sum > 0 else -1
                    return True
            sum_cross_1 = np.diag(self.board[:, y]).sum()  # 対角成分
            if np.abs(sum_cross_1) == self.board_size:
                self.reward = 1 if sum_cross_1 > 0 else -1
                return True
            sum_cross_2 = np.diag(np.fliplr(self.board[:, y])).sum()   # 左下から右上の要素の合計
            if np.abs(sum_cross_2) == self.board_size:
                self.reward = 1 if sum_cross_2 > 0 else -1
                return True
        for z in range(self.board_size):
            for x in range(self.board_size):
                sum = self.board[x, :, z].sum()     # 足すことで全部白か黒か判定可能
                if np.abs(sum) == self.board_size:
                    self.reward = 1 if sum > 0 else -1  # メソッド化すべき
                    return True
            for y in range(self.board_size):
                sum = self.board[:, y, z].sum()
                if np.abs(sum) == self.board_size:
                    self.reward = 1 if sum > 0 else -1
                    return True
            sum_cross_1 = np.diag(self.board[:, :, z]).sum()  # 対角成分
            if np.abs(sum_cross_1) == self.board_size:
                self.reward = 1 if sum_cross_1 > 0 else -1
                return True
            sum_cross_2 = np.diag(np.fliplr(self.board[:, :, z])).sum()   # 左下から右上の要素の合計
            if np.abs(sum_cross_2) == self.board_size:
                self.reward = 1 if sum_cross_2 > 0 else -1
                return True
        sum_cross_1 = np.array([self.board[i, i, i] for i in range(self.board_size)]).sum()
        if np.abs(sum_cross_1) == self.board_size:
            self.reward = 1 if sum_cross_1 > 0 else -1
            return True
        sum_cross_2 = np.array([self.board[i, i, self.board_size - i - 1] for i in range(self.board_size)]).sum()
        if np.abs(sum_cross_2) == self.board_size:
            self.reward = 1 if sum_cross_2 > 0 else -1
            return True
        sum_cross_3 = np.array([self.board[i, self.board_size - i - 1, i] for i in range(self.board_size)]).sum()
        if np.abs(sum_cross_3) == self.board_size:
            self.reward = 1 if sum_cross_3 > 0 else -1
            return True
        sum_cross_4 = np.array([self.board[i, self.board_size - i - 1, self.board_size - i - 1] for i in range(self.board_size)]).sum()
        if np.abs(sum_cross_4) == self.board_size:
            self.reward = 1 if sum_cross_4 > 0 else -1
            return True
        return False