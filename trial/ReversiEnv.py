import gymnasium as gym
from gymnasium import spaces
import numpy as np

class ReversiEnv(gym.Env):
    metadata = {"render_modes": ["human"]}
    
    def __init__(self, render_mode=None):
        super().__init__()
        self.board_size = 8
        # 観測空間: 8x8のマス、各マスは {空=0, 黒=1, 白=-1} とする
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.board_size, self.board_size), dtype=int)
        # 行動空間: 64マスのいずれかに打つことを選択(0~63)
        self.action_space = spaces.Discrete(self.board_size * self.board_size)
        
        # 内部状態
        self.board = None
        self.current_player = 1  # 黒=1, 白=-1
        self.render_mode = render_mode
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        # 初期配置(中央4マス)
        mid = self.board_size // 2
        self.board[mid-1, mid-1] = 1
        self.board[mid-1, mid] = -1
        self.board[mid, mid-1] = -1
        self.board[mid, mid] = 1
        self.current_player = 1
        observation = self.board.copy()
        info = {}
        return observation, info
    
    def step(self, action):
        # actionは0~63の整数, これをボード上の(i,j)にマッピング
        i = action // self.board_size
        j = action % self.board_size
        
        # 行動が有効か判定
        if not self.is_valid_move(i, j, self.current_player):
            # 無効手を打った場合は大きな負の報酬を与え、エピソード終了とするなどの処理を行う
            # ここでは簡易的に、報酬=-1でゲーム終了
            reward = -1
            terminated = True
            info = {"illegal_move": True}
            return self.board.copy(), reward, terminated, False, info
        
        # 石を置く
        self.place_disc(i, j, self.current_player)
        
        # 次のプレイヤーへ
        self.current_player *= -1
        
        # 相手の行動(ここではランダム)
        self.opponent_move()
        
        # 終了判定
        terminated = self.is_game_over()
        if terminated:
            reward = self.compute_final_reward()
        else:
            reward = 0.0
        
        info = {}
        return self.board.copy(), reward, terminated, False, info

    def is_valid_move(self, i, j, player):
        # ボード外、既に埋まっているマスは×
        if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size:
            return False
        if self.board[i, j] != 0:
            return False
        
        # ひっくり返せる石があるか確認
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        opponent = -player
        for di, dj in directions:
            x, y = i+di, j+dj
            found_opponent = False
            while 0 <= x < self.board_size and 0 <= y < self.board_size:
                if self.board[x, y] == opponent:
                    found_opponent = True
                    x += di
                    y += dj
                elif self.board[x, y] == player and found_opponent:
                    return True
                else:
                    break
        return False

    def place_disc(self, i, j, player):
        self.board[i, j] = player
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        opponent = -player
        for di, dj in directions:
            x, y = i+di, j+dj
            stones_to_flip = []
            while 0 <= x < self.board_size and 0 <= y < self.board_size:
                if self.board[x, y] == opponent:
                    stones_to_flip.append((x, y))
                    x += di
                    y += dj
                elif self.board[x, y] == player:
                    # 間に挟まれた相手石を反転
                    for (fx, fy) in stones_to_flip:
                        self.board[fx, fy] = player
                    break
                else:
                    break

    def opponent_move(self):
        # シンプルに相手はランダムで有効手を打つ
        valid_moves = []
        for pos in range(self.board_size * self.board_size):
            i = pos // self.board_size
            j = pos % self.board_size
            if self.is_valid_move(i, j, self.current_player):
                valid_moves.append(pos)
        if valid_moves:
            chosen = np.random.choice(valid_moves)
            i = chosen // self.board_size
            j = chosen % self.board_size
            self.place_disc(i, j, self.current_player)
        self.current_player *= -1

    def is_game_over(self):
        # 黒、白双方が打てる手がない場合 or 全マス埋まり
        if np.all(self.board != 0):
            return True
        # 黒の手番で有効手がないか
        if not any(self.is_valid_move(i,j,1) for i in range(self.board_size) for j in range(self.board_size)):
            # 白の手番で有効手がないか
            if not any(self.is_valid_move(i,j,-1) for i in range(self.board_size) for j in range(self.board_size)):
                return True
        return False

    def compute_final_reward(self):
        # 黒=1, 白=-1 とし、最終的に黒が多ければ+1、負ければ-1、同数なら0
        black_count = np.sum(self.board == 1)
        white_count = np.sum(self.board == -1)
        if black_count > white_count:
            return 1.0
        elif black_count < white_count:
            return -1.0
        else:
            return 0.0

    def render(self):
        if self.render_mode == "human":
            print(self.board)
