import gymnasium as gym
from gymnasium import spaces
import numpy as np

class Environment(gym.Env):
    metadata = {"render_modes": ["human"]}

    # クラスのインスタンス化時に呼ばれるメソッド(=コンストラクタ)
    # 盤面の設定や黒が先手などの設定を行う
    def __init__(self, render_mode=None):
        super().__init__()
        self.board_size = 4
        # 4 x 4 x 4 のマス，各マスは {空=0, 黒=1, 白=-1} とする
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.board_size, self.board_size, self.board_size), dtype=int)
        # 行動空間: 64マスのいずれかに打つことを選択(0~63)
        self.action_space = spaces.Discrete(self.board_size * self.board_size * self.board_size)

        # 内部状態
        self.board = None
        self.current_player = 1  # 黒=1, 白=-1
        self.render_mode = render_mode

    # 環境の初期化
    ## 4 x 4 x 4 のマスを全て0にし，手番を黒にする
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # 初期配置
        self.board = np.zeros((self.board_size, self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        observation = self.board.copy()
        info = {}
        return observation, info
    
    # 行動の実行
    def step(self, action):
        pass
        