from Opponent import Opponent
import numpy as np

class RandomOpponent(Opponent):
    def __init__(self, env):
        self.env = env
    def opponent_move(self, board):
        valid_moves = []
        for pos in range(self.env.board_size * self.env.board_size * self.env.board_size):
            i = pos // (self.env.board_size * self.env.board_size)
            j = (pos // self.env.board_size) % self.env.board_size
            k = pos % self.env.board_size
            if self.env.is_valid_move(i, j, k, self.env.current_player):
                valid_moves.append(pos)
                
        if valid_moves:
            chosen = np.random.choice(valid_moves)
            i = chosen // (self.env.board_size * self.env.board_size)
            j = (chosen  // self.env.board_size) % self.env.board_size
            k = chosen % self.env.board_size
            return (i, j, k)
        else:
            return (-1, -1, -1)     # 置けるところがない場合は不正値を返す